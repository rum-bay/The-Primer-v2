# Release & deployment plan

## v2.0 changes

The starter demo becomes **The Primer**, a short software-engineering story whose tutor behavior is driven by a small sklearn logistic-regression model. The contract is `model.onnx` + `config.json`; the browser loads and executes ONNX locally. The current training CSV is synthetic, so this build is a reproducible prototype and is not yet a qualified release for real learners.

The course brief permits synthetic-only data and awards half credit for that rubric item. If no volunteers are available, `publish_hf.py <repo> --synthetic-demo` explicitly publishes a classroom demo. The Hub model card retains the synthetic source and states that real-learner performance has not been validated. Do not describe simulated sessions as real participants.

## Version identity and pinned model URL

- Model repository: **pending team Hugging Face account and public upload**.
- Hub commit: **pending upload**. Do not replace this placeholder with `main`.
- Required consumer URL after upload: `https://huggingface.co/<owner>/<repo>/resolve/<40-character-HF-commit>/model.onnx`.
- Record the same commit in `web/site.json` and the submission form. `main` is mutable and must not be used by deployed consumers.
- Previous version/rollback commit: **pending first public v2 release**. Retain the preceding model and `config.json` commit. Roll back by restoring that pinned URL in `web/site.json`, redeploying Pages, and checking all five parity cases.

## Safe activation

1. **Shadow:** for a real-data release, collect at least 15 real sessions and retrain behind the written `spec.md` gates before comparing v2 with the current model on consented inputs. A synthetic-only build is a classroom demo; keep its source label visible and do not treat shadow metrics as real-user validation. Compare probabilities, calibration and hint rate; log aggregate metrics only.
2. **Canary (5%):** expose v2 to a consenting 5% of test participants, still with an obvious opt-out. Check inference failures, completion rate, hint rate, and qualitative feedback against the prior release. Stop on crash/regression or if hint rate moves by more than 10 percentage points without explanation.
3. **Progressive rollout:** increase 25% → 50% → 100%, holding each stage for at least one review cycle and checking the same measures. Preserve the previous pinned URL throughout.
4. **Rollback:** if parity, E2E regression, error rate, or participant feedback fails, restore the previous commit-pinned model URL and web build. Re-run `python tests/parite.py` and the Cypress suite before a new canary.

These are proposed procedures; no canary or public rollout has been performed from this workspace.

## Architecture trade-offs

| Runtime | Network / latency | Does player data leave device? | Model secrecy / REA exposure |
|---|---|---|---|
| **Browser, `onnxruntime-web` (selected)** | First load downloads ONNX + WASM; later inference is local and low latency. The story still works after loading while offline. | No: feature rows and predictions stay in the browser; downloading the public model contacts Hub once. | No secrecy: users can save/reverse engineer a public ONNX model. Appropriate for this non-sensitive classroom model. |
| Mobile, `onnxruntime-react-native` | Bundled model: offline and low latency; remote update needs network. | No for bundled/remote on-device inference. | Public if bundled/downloaded; binary inspection is possible. |
| Server API, e.g. Render + FastAPI / ONNX Runtime | Every prediction needs network and incurs request latency/availability risk. | Yes: inputs leave the device and reach the server; TLS, retention, consent and access control would be needed. | Weights can remain server-side, but repeated input/output queries still create model-extraction / REA risk. |

The browser option is selected because it matches the current data-minimization goal and the starter repository's `onnxruntime-web` consumer. Its explicit cost is public model weights and initial download time.

## Release checklist

- [ ] Choose one honest data route: add/disclose at least 15 real sessions for full data credit, or use the permitted synthetic-only route and accept half credit for the data rubric item.
- [ ] Pass fixed evaluation thresholds and ONNX parity.
- [ ] Push model files to a public HF repo; record the exact commit hash above and in `web/site.json`. Use `--synthetic-demo` when fewer than 15 real sessions are present.
- [ ] Publish the web app to GitHub Pages; verify in a private/incognito window.
- [ ] Run Cypress regression and Python parity tests against the release.
- [ ] Include a 60–90 second A/B demo. If it is simulated, keep the simulation label visible and disclose it in `DELIVERY_CHECKLIST.md`; if the rubric strictly requires a live app screen capture, record one separately. `demo-simule.mp4` is a 70-second illustrated synthetic demo, not a live screen capture.
