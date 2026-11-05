"""Regenerate the five frozen ONNX oracle probabilities after an accepted retrain."""
import json
from pathlib import Path
import numpy as np
import onnxruntime as ort

ROOT = Path(__file__).resolve().parents[1]
cfg = json.loads((ROOT / "model/config.json").read_text(encoding="utf-8"))
sess = ort.InferenceSession(str(ROOT / "model/model.onnx"), providers=["CPUExecutionProvider"])
cases = []
for i, values in enumerate(cfg["reference_inputs"], 1):
    x = np.asarray([values], dtype=np.float32)
    p = sess.run(["probabilities"], {"input": x})[0][0].astype(float).tolist()
    cases.append({"id": f"case-{i}", "input": dict(zip([f["name"] for f in cfg["features"]], values)), "probabilities": p})
(ROOT / "tests/parite.json").write_text(json.dumps({"tolerance": 1e-4, "cases": cases}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote 5 ONNX oracle fixtures")
