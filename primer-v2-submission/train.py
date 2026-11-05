"""Deterministic sklearn training, acceptance gate, and sklearn→ONNX export."""
from __future__ import annotations

import json
import hashlib
import importlib.machinery
import importlib.metadata
import shutil
import sys
import tempfile
import types
from pathlib import Path

import numpy as np
import pandas as pd
import sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import balanced_accuracy_score, brier_score_loss, roc_auc_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "oturumlar.csv"
DEST = ROOT / "model"
SEED = 13
SYNTHETIC_SEED = 20261105
FEATURES = [
    "bekleme_suresi_sn", "karar_degistirme", "tekrar_okuma", "onceki_yanlis",
    "onceki_ipucu", "zorluk", "dal_kodu",
]
GATES = {"balanced_accuracy_min": 0.62, "roc_auc_min": 0.68, "brier_max": 0.24}
PREDICTION_THRESHOLD = 0.55
MIN_REAL_SESSIONS_FOR_RELEASE = 15


def main() -> None:
    if not DATA.exists():
        raise SystemExit(f"Veri yok: {DATA}; önce CSV'yi hazırlayın.")
    df = pd.read_csv(DATA)
    required = {"oturum_id", "ipucu_istendi", "kaynak", *FEATURES}
    missing = required - set(df.columns)
    if missing:
        raise SystemExit(f"Eksik sütunlar: {sorted(missing)}")
    if not set(df["kaynak"].dropna().unique()) <= {"gercek", "sentetik"}:
        raise SystemExit("kaynak yalnızca gercek veya sentetik olabilir.")
    if df[list(required)].isna().any().any():
        raise SystemExit("Gerekli sütunlarda boş değer var.")
    y = df["ipucu_istendi"].astype(int)
    if set(y.unique()) != {0, 1}:
        raise SystemExit("Eğitim için iki hedef sınıfın da bulunması gerekir.")
    if df["oturum_id"].nunique() < 8:
        raise SystemExit("Group holdout için en az 8 farklı oturum gerekir.")

    splitter = GroupShuffleSplit(n_splits=1, test_size=0.25, random_state=SEED)
    train_idx, test_idx = next(splitter.split(df, y, groups=df["oturum_id"]))
    X_train, X_test = df.iloc[train_idx][FEATURES], df.iloc[test_idx][FEATURES]
    y_train, y_test = y.iloc[train_idx], y.iloc[test_idx]
    model = Pipeline([
        ("scaler", StandardScaler()),
        ("lr", LogisticRegression(random_state=SEED, max_iter=1000)),
    ])
    model.fit(X_train, y_train)
    proba = model.predict_proba(X_test)[:, 1]
    metrics = {
        "balanced_accuracy": round(float(balanced_accuracy_score(y_test, proba >= PREDICTION_THRESHOLD)), 6),
        "roc_auc": round(float(roc_auc_score(y_test, proba)), 6),
        "brier_score": round(float(brier_score_loss(y_test, proba)), 6),
        "train_decisions": int(len(train_idx)), "test_decisions": int(len(test_idx)),
        "train_sessions": int(df.iloc[train_idx]["oturum_id"].nunique()),
        "test_sessions": int(df.iloc[test_idx]["oturum_id"].nunique()),
        "class_1_rate_test": round(float(y_test.mean()), 6),
    }
    real_sessions = int(df.loc[df["kaynak"] == "gercek", "oturum_id"].nunique())
    synthetic_sessions = int(df.loc[df["kaynak"] == "sentetik", "oturum_id"].nunique())
    failed = []
    if metrics["balanced_accuracy"] < GATES["balanced_accuracy_min"]:
        failed.append("balanced_accuracy")
    if metrics["roc_auc"] < GATES["roc_auc_min"]:
        failed.append("roc_auc")
    if metrics["brier_score"] > GATES["brier_max"]:
        failed.append("brier_score")
    print("Group holdout metrics:", json.dumps(metrics, ensure_ascii=False))
    if failed:
        raise SystemExit("EVAL GATE FAILED; model artifacts were not written: " + ", ".join(failed))

    import onnxruntime as ort
    import scipy
    skl2onnx_version = importlib.metadata.version("skl2onnx")
    onnx_version = importlib.metadata.version("onnx")

    stage = Path(tempfile.mkdtemp(prefix="primer-model-", dir=ROOT))
    try:
        onx_bytes, exporter = export_sklearn_model(model, len(FEATURES))
        onnx_path = stage / "model.onnx"
        onnx_path.write_bytes(onx_bytes)
        session = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
        x_check = X_test.to_numpy(dtype=np.float32)
        onnx_proba = session.run(["probabilities"], {"input": x_check})[0]
        sklearn_proba = model.predict_proba(X_test)
        parity = float(np.max(np.abs(onnx_proba - sklearn_proba)))
        if parity >= 1e-4:
            raise SystemExit(f"EVAL GATE FAILED; sklearn/ONNX max difference {parity:.3g} >= 1e-4")

        examples = [
            [1.2, 0, 0, 0, 0, 1, 1], [8.0, 1, 0, 0, 0, 2, 0],
            [14.0, 2, 1, 1, 0, 3, 0], [20.0, 3, 2, 2, 1, 4, 1],
            [5.5, 0, 1, 1, 2, 5, 2],
        ]
        config = {
            "title": "The Primer v2 — uyarlanabilir tutor",
            "description": "Sentetik başlangıç verisiyle eğitilmiş, demo amaçlı küçük lojistik regresyon modeli.",
            "target": "ipucu_istendi",
            "model_version": "2.0.0",
            "classes": ["0", "1"],
            "class_labels": {"0": "İpucu istemedi", "1": "İpucu istedi"},
            "features": [{"name": name, "label": label} for name, label in zip(FEATURES, [
                "Karar süresi (sn)", "Karar değiştirme sayısı", "Tekrar okuma sayısı",
                "Önceki yanlış sayısı", "Önceki tutor ipucu sayısı", "Sahne zorluğu (1–5)",
                "Seçilen dal kodu (0–2)",
            ])],
            "input": {"name": "input", "dtype": "float32", "shape": [None, len(FEATURES)]},
            "output": {"name": "probabilities", "dtype": "float32", "shape": [None, 2]},
            "prediction_threshold": PREDICTION_THRESHOLD,
            "request_schema": {
                "type": "object",
                "properties": {name: {"type": "number"} for name in FEATURES},
                "required": FEATURES,
                "additionalProperties": False,
            },
            "response_schema": {
                "type": "object",
                "properties": {"probabilities": {"type": "array", "items": {"type": "number"}, "minItems": 2, "maxItems": 2}},
                "required": ["probabilities"],
                "additionalProperties": False,
            },
            "metrics": metrics,
            "acceptance_gates": GATES,
            "onnx_max_abs_diff": parity,
            "onnx_exporter": exporter,
            "seed": SEED,
            "synthetic_data_seed": SYNTHETIC_SEED,
            "evaluation_split": {
                "method": "GroupShuffleSplit",
                "test_size": 0.25,
                "random_state": SEED,
                "group_column": "oturum_id",
            },
            "sklearn_version": sklearn.__version__,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "dependencies": {
                "numpy": np.__version__, "pandas": pd.__version__, "scipy": scipy.__version__,
                "scikit-learn": sklearn.__version__, "skl2onnx": skl2onnx_version,
                "onnx": onnx_version, "onnxruntime": ort.__version__,
            },
            "data_sources": {str(k): int(v) for k, v in df["kaynak"].value_counts().items()},
            "data_source_sessions": {str(k): int(v) for k, v in df.groupby("kaynak")["oturum_id"].nunique().items()},
            "real_sessions": real_sessions,
            "synthetic_sessions": synthetic_sessions,
            "min_real_sessions_for_release": MIN_REAL_SESSIONS_FOR_RELEASE,
            "evaluation_gates_passed": True,
            "onnx_parity_passed": parity < 1e-4,
            "real_data_ready": real_sessions >= MIN_REAL_SESSIONS_FOR_RELEASE,
            "synthetic_demo_ready": synthetic_sessions > 0,
            "release_ready": real_sessions >= MIN_REAL_SESSIONS_FOR_RELEASE,
            "data_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
            "onnx_sha256": hashlib.sha256(onnx_path.read_bytes()).hexdigest(),
            "reference_inputs": examples,
        }
        (stage / "config.json").write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (stage / "README.md").write_text(model_card(config), encoding="utf-8")
        if DEST.exists():
            shutil.rmtree(DEST)
        stage.replace(DEST)
        print(f"Eval gate passed; model.onnx, config.json, README.md -> {DEST}; parity max={parity:.2e}")
    finally:
        if stage.exists():
            shutil.rmtree(stage)


def model_card(c: dict) -> str:
    m = c["metrics"]
    return f"""# Model card — The Primer v2 tutor preference

## Purpose
Predict whether a player would self-report wanting an explanation after an interactive story decision. Probability ≥ {c['prediction_threshold']:.2f} adds an optional tutor note and removes the next scene's time pressure.

## Data
This artifact uses {c['data_sources'].get('gercek', 0)} real and {c['data_sources'].get('sentetik', 0)} synthetic decision rows ({c['real_sessions']} real sessions; synthetic generator seed {c['synthetic_data_seed']}). The synthetic rule is a simulator, not evidence about people. Real-data release-ready: **{str(c['release_ready']).lower()}**. Synthetic classroom-demo eligible: **{str(c['synthetic_demo_ready']).lower()}** when the evaluation and ONNX parity gates pass. The course brief permits synthetic-only work but awards half credit for the data item; any public demo must remain labelled synthetic and must not be described as validated on real learners.

## Evaluation
Group holdout by session (seed {c['seed']}); balanced accuracy {m['balanced_accuracy']:.4f}; ROC AUC {m['roc_auc']:.4f}; Brier score {m['brier_score']:.4f}; sklearn→ONNX max probability difference {c['onnx_max_abs_diff']:.2e}. Acceptance gates declared before training: balanced accuracy ≥ 0.62, ROC AUC ≥ 0.68, Brier score ≤ 0.24.

## Limits and prohibited use
Classroom prototype only. Do not grade, diagnose, profile, or make consequential decisions about learners. Synthetic validation does not establish real-world accuracy; collect consented real sessions, re-evaluate, and replace this model before making claims. Inputs omit identity and demographics. The browser model is public.
"""


def export_sklearn_model(model: Pipeline, feature_count: int) -> tuple[bytes, str]:
    """Prefer skl2onnx; fall back to an equivalent pure-protobuf logistic graph.

    The fallback avoids loading ONNX's optional native helper extension, which
    may be denied by Windows application-control policy. ONNX Runtime still
    validates and executes the serialized graph before release artifacts exist.
    """
    try:
        from skl2onnx import to_onnx
        from skl2onnx.common.data_types import FloatTensorType
        onx = to_onnx(
            model,
            initial_types=[("input", FloatTensorType([None, feature_count]))],
            options={id(model): {"zipmap": False}},
            target_opset=17,
        )
        return onx.SerializeToString(), "skl2onnx"
    except (ImportError, OSError):
        return _serialize_logistic_onnx(model, feature_count), "primer-protobuf-logistic-fallback"


def _serialize_logistic_onnx(model: Pipeline, feature_count: int) -> bytes:
    """Serialize StandardScaler + binary LogisticRegression as core ONNX ops."""
    import importlib

    onnx_dir = Path(importlib.metadata.distribution("onnx").locate_file("onnx"))
    for module_name in list(sys.modules):
        if module_name == "onnx" or module_name.startswith("onnx."):
            del sys.modules[module_name]
    package = types.ModuleType("onnx")
    package.__path__ = [str(onnx_dir)]
    package.__package__ = "onnx"
    package.__spec__ = importlib.machinery.ModuleSpec("onnx", loader=None, is_package=True)
    sys.modules["onnx"] = package
    proto = importlib.import_module("onnx.onnx_ml_pb2")
    AttributeProto = proto.AttributeProto
    GraphProto = proto.GraphProto
    ModelProto = proto.ModelProto
    NodeProto = proto.NodeProto
    TensorProto = proto.TensorProto
    ValueInfoProto = proto.ValueInfoProto

    def tensor(name: str, values, dims: list[int]):
        value = TensorProto(name=name, data_type=TensorProto.FLOAT)
        value.dims.extend(dims)
        value.float_data.extend(np.asarray(values, dtype=np.float32).ravel().tolist())
        return value

    def value_info(name: str, width: int):
        value = ValueInfoProto(name=name)
        value.type.tensor_type.elem_type = TensorProto.FLOAT
        value.type.tensor_type.shape.dim.add().dim_param = "N"
        value.type.tensor_type.shape.dim.add().dim_value = width
        return value

    def node(op: str, name: str, inputs: list[str], outputs: list[str], axis: int | None = None):
        value = NodeProto(op_type=op, name=name)
        value.input.extend(inputs)
        value.output.extend(outputs)
        if axis is not None:
            attr = value.attribute.add(name="axis")
            attr.type = AttributeProto.INT
            attr.i = axis
        return value

    scaler = model.named_steps["scaler"]
    lr = model.named_steps["lr"]
    graph = GraphProto(name="primer_binary_logistic")
    graph.input.add().CopyFrom(value_info("input", feature_count))
    graph.output.add().CopyFrom(value_info("probabilities", 2))
    graph.initializer.extend([
        tensor("mean", scaler.mean_, [feature_count]),
        tensor("scale", scaler.scale_, [feature_count]),
        tensor("coefficients", lr.coef_[0].reshape(-1, 1), [feature_count, 1]),
        tensor("intercept", lr.intercept_, [1]),
        tensor("one", [1.0], [1]),
    ])
    graph.node.extend([
        node("Sub", "center", ["input", "mean"], ["centered"]),
        node("Div", "standardize", ["centered", "scale"], ["scaled"]),
        node("Gemm", "linear", ["scaled", "coefficients", "intercept"], ["logit"]),
        node("Sigmoid", "positive_probability", ["logit"], ["p1"]),
        node("Sub", "negative_probability", ["one", "p1"], ["p0"]),
        node("Concat", "class_probabilities", ["p0", "p1"], ["probabilities"], axis=1),
    ])
    model_proto = ModelProto(
        ir_version=10,
        producer_name="The Primer sklearn logistic exporter",
        producer_version="1.0.0",
    )
    model_proto.graph.CopyFrom(graph)
    opset = model_proto.opset_import.add()
    opset.domain = ""
    opset.version = 17
    return model_proto.SerializeToString()


if __name__ == "__main__":
    main()
