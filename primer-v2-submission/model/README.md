# Model card — The Primer v2 tutor preference

## Purpose
Predict whether a player would self-report wanting an explanation after an interactive story decision. Probability ≥ 0.55 adds an optional tutor note and removes the next scene's time pressure.

## Data
This artifact uses 0 real and 240 synthetic decision rows (0 real sessions; synthetic generator seed 20261105). The synthetic rule is a simulator, not evidence about people. Real-data release-ready: **false**. Synthetic classroom-demo eligible: **true** when the evaluation and ONNX parity gates pass. The course brief permits synthetic-only work but awards half credit for the data item; any public demo must remain labelled synthetic and must not be described as validated on real learners.

## Evaluation
Group holdout by session (seed 13); balanced accuracy 0.7031; ROC AUC 0.7746; Brier score 0.1934; sklearn→ONNX max probability difference 9.46e-08. Acceptance gates declared before training: balanced accuracy ≥ 0.62, ROC AUC ≥ 0.68, Brier score ≤ 0.24.

## Limits and prohibited use
Classroom prototype only. Do not grade, diagnose, profile, or make consequential decisions about learners. Synthetic validation does not establish real-world accuracy; collect consented real sessions, re-evaluate, and replace this model before making claims. Inputs omit identity and demographics. The browser model is public.
