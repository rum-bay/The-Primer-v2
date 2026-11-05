"""Upload the accepted ONNX model to a public HF repo and pin the web manifest."""
from __future__ import annotations
import json
import hashlib
import re
import sys
import csv
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def main() -> None:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repo_id", help="Hugging Face repo, ör. kullanici/the-primer-v2")
    parser.add_argument("--synthetic-demo", action="store_true",
                        help="15 gerçek oturum olmadan, açıkça sentetik/sınıf demosu olarak yayınla")
    parser.add_argument("--dry-run", action="store_true", help="kapıları doğrula, Hub'a yükleme yapma")
    args = parser.parse_args()
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", args.repo_id):
        raise SystemExit("Repo adı şu biçimde olmalı: hf-kullanici/the-primer-v2")
    repo_id = args.repo_id
    with (ROOT / "data" / "oturumlar.csv").open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    real_sessions = {row["oturum_id"] for row in rows if row["kaynak"] == "gercek"}
    synthetic_sessions = {row["oturum_id"] for row in rows if row["kaynak"] == "sentetik"}
    model_dir = ROOT / "model"
    for filename in ("model.onnx", "config.json", "README.md"):
        if not (model_dir / filename).is_file():
            raise SystemExit(f"Model artefaktı eksik: {model_dir / filename}")
    config = json.loads((model_dir / "config.json").read_text(encoding="utf-8"))
    current_data_hash = hashlib.sha256((ROOT / "data" / "oturumlar.csv").read_bytes()).hexdigest()
    if config.get("data_sha256") != current_data_hash:
        raise SystemExit("Yayın durduruldu: model artefaktı güncel oturumlar.csv ile eğitilmemiş; train.py'yi yeniden çalıştırın.")
    gates_passed = config.get("evaluation_gates_passed", False) and config.get("onnx_parity_passed", False)
    real_ready = len(real_sessions) >= 15 and config.get("release_ready", False) and gates_passed
    synthetic_demo_ready = (
        args.synthetic_demo and bool(synthetic_sessions)
        and config.get("synthetic_demo_ready", False) and gates_passed
    )
    if not real_ready and not synthetic_demo_ready:
        if len(real_sessions) < 15:
            raise SystemExit(
                f"15 gerçek oturum yok (mevcut: {len(real_sessions)}). Ödevin izin verdiği sentetik demo için "
                "`--synthetic-demo` kullanın; veri puanının yarısı uygulanır ve sentetik kaynak açıkça belirtilir."
            )
        raise SystemExit("Yayın durduruldu: eval/parite kapısı geçmemiş veya güncel model artefaktı hazır değil.")
    publication_mode = "real-data release" if real_ready else "synthetic classroom demo (not validated on real learners)"
    if args.dry_run:
        print(f"DRY RUN PASS: {publication_mode}")
        print(f"Data: {len(real_sessions)} real sessions, {len(synthetic_sessions)} synthetic sessions")
        print("No files uploaded; no Hub repo created.")
        return
    from huggingface_hub import HfApi
    api = HfApi()
    api.create_repo(repo_id=repo_id, repo_type="model", private=False, exist_ok=True)
    commit = api.upload_folder(repo_id=repo_id, repo_type="model", folder_path=str(model_dir),
                               commit_message=f"The Primer v2 {publication_mode} ONNX model")
    revision = commit.oid
    manifest = {
        "model_repo": repo_id,
        "revision": revision,
        "publication_mode": "real-data" if real_ready else "synthetic-demo",
        "model_url": f"https://huggingface.co/{repo_id}/resolve/{revision}/model.onnx",
        "config_url": f"https://huggingface.co/{repo_id}/resolve/{revision}/config.json",
    }
    (ROOT / "web" / "site.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    release_path = ROOT / "RELEASE.md"
    release = release_path.read_text(encoding="utf-8")
    if "## Publication mode" not in release:
        release = release.replace(
            "## Version identity and pinned model URL",
            "## Publication mode\n\n- Published mode: **" + publication_mode + "**.\n- Data sources: "
            + str(len(real_sessions)) + " real sessions, " + str(len(synthetic_sessions))
            + " synthetic sessions. Synthetic data receives half credit for the data rubric item and is not evidence of real learner behavior.\n\n"
            + "## Version identity and pinned model URL",
        )
    release = release.replace("- Model repository: **pending team Hugging Face account and public upload**.",
                              f"- Model repository: https://huggingface.co/{repo_id}")
    release = release.replace("- Hub commit: **pending upload**. Do not replace this placeholder with `main`.",
                              f"- Hub commit: `{revision}`. Consumers use the immutable commit.")
    release = release.replace("- Required consumer URL after upload: `https://huggingface.co/<owner>/<repo>/resolve/<40-character-HF-commit>/model.onnx`.",
                              f"- Consumer URL: `{manifest['model_url']}`")
    release_path.write_text(release, encoding="utf-8")
    print(f"HF model: https://huggingface.co/{repo_id}")
    print(f"Pinned ONNX: {manifest['model_url']}")
    print(f"Revision: {revision}")
    print(f"Publication mode: {publication_mode}")
    print("`web/site.json` güncellendi; şimdi GitHub repo'ya commit/push edin.")

if __name__ == "__main__":
    main()
