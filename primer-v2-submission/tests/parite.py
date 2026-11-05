"""Oracle: run the exact ONNX artifact with ONNX Runtime Python."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).resolve().parents[1]
CONFIG, MODEL, FIXTURES = ROOT / "model/config.json", ROOT / "model/model.onnx", ROOT / "tests/parite.json"
TOLERANCE = 1e-4

def main() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    reference = json.loads(FIXTURES.read_text(encoding="utf-8"))
    if len(reference["cases"]) != 5:
        raise SystemExit("parite.json tam olarak 5 referans girdi içermeli")
    session = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    failures = []
    for case in reference["cases"]:
        names = [f["name"] for f in cfg["features"]]
        row = np.asarray([[case["input"][name] for name in names]], dtype=np.float32)
        observed = session.run(["probabilities"], {"input": row})[0][0]
        expected = np.asarray(case["probabilities"], dtype=np.float64)
        diff = float(np.max(np.abs(observed.astype(np.float64) - expected)))
        print(f"{case['id']}: max_abs_diff={diff:.2e}")
        if diff >= TOLERANCE:
            failures.append(case["id"])
    if failures:
        raise SystemExit("parity failed: " + ", ".join(failures))
    print("PASS: 5/5 Python ONNX oracle cases pass")

if __name__ == "__main__":
    main()
