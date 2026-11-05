# The Primer v2 — model spec

## Problem and intended behavior

The Primer is a short story for a person learning software engineering. At each decision it predicts whether the player would ask for an explanation, based only on interaction behavior observed so far. If `P(ipucu_istendi=1) >= 0.55`, the next scene adds a tutor explanation and removes its visible 30-second countdown. Below the threshold, it keeps the concise story and countdown. A prediction is a hint preference, not a measure of intelligence or ability. Inference does not update model weights; new consented rows are used only in a later offline retraining run.

## Contract

- Tabular binary classification; a fitted `sklearn.pipeline.Pipeline(StandardScaler, LogisticRegression)` exported to ONNX. `train.py` uses `skl2onnx`; if the host blocks its ONNX native helper, it serializes the mathematically equivalent scaler/logistic graph with ONNX protobuf and validates it with ONNX Runtime.
- Feature order, float32 input tensor name `input`, output `probabilities`, and labels are declared in `model/config.json`.
- Features: `bekleme_suresi_sn`, `karar_degistirme`, `tekrar_okuma`, `onceki_yanlis`, `onceki_ipucu`, `zorluk`, `dal_kodu`.
- Target: `ipucu_istendi` (0/1, a player's explicit, optional self-report after a decision).
- Seed: 13 for split and model, and a separately documented seed for synthetic-data generation.
- Inference parity tolerance: maximum absolute probability difference `< 1e-4`.

## Evaluation and release gate (written before training)

Group holdout by session prevents decisions from one session appearing in both train and test. Release only if all three test-set criteria pass:

1. Balanced accuracy `>= 0.62`.
2. ROC AUC `>= 0.68`.
3. Brier score `<= 0.24`.

The thresholds are engineering gates for this small classroom prototype, not evidence of performance with real learners. `train.py` stops before writing release artifacts if a gate or ONNX parity check fails.

## Three acceptance examples

1. A long pause, several changed choices, and rereads produce a higher support probability than a quick, unchanged decision with the same difficulty.
2. At a prediction of `0.55` or higher, the game must show a tutor explanation and switch off the next scene's time pressure; below it, it must use the concise version.
3. Python ONNX and browser ONNX inference on each of the five reference inputs must differ by less than `1e-4`, and completing 21 decisions must preserve the pre-model story flow.

## Data and limits

The checked-in CSV is synthetic. Its labels are produced by the documented simulator rule, not provided by actual players; in live data-collection mode the label is a player's explicit self-report. No real-person sessions have been collected in this workspace. The course brief permits synthetic-only submissions but awards half credit for the data rubric item, so this project does not claim the full real-data item. No name, email, device ID, or location is requested or stored. The synthetic data generator and seed are documented in `README.md`.

The model may overfit synthetic behavior. It must not grade students, diagnose needs, or be used to make consequential decisions. A participant can ignore a hint or stop at any time.
