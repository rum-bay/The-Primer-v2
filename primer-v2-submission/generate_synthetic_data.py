"""Create a reproducible, explicitly synthetic starter dataset (never real user data)."""
from __future__ import annotations

import csv
import math
import random
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "data" / "sentetik.csv"
SEED = 20261105
FEATURES = [
    "bekleme_suresi_sn", "karar_degistirme", "tekrar_okuma", "onceki_yanlis",
    "onceki_ipucu", "zorluk", "dal_kodu",
]
FIELDS = ["oturum_id", "karar_no", *FEATURES, "ipucu_istendi", "kaynak"]


def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))


def main() -> None:
    rng = random.Random(SEED)
    rows = []
    for person in range(48):
        session_id = str(uuid.UUID(int=rng.getrandbits(128)))
        wait_bias = rng.gauss(0, 2.0)
        hint_count = wrong_count = 0
        for decision_no in range(1, 6):
            difficulty = 1 + (decision_no - 1) % 5
            wait_s = round(max(0.2, min(30.0, rng.gauss(6.0 + difficulty * 1.3 + wait_bias, 4.0))), 2)
            changes = max(0, min(4, int(rng.gauss(0.35 + wait_s / 10, 0.9))))
            rereads = max(0, min(3, int(rng.gauss(0.1 + wait_s / 14, 0.8))))
            branch = rng.randrange(3)
            logit = (-2.45 + 0.095 * wait_s + 0.53 * changes + 0.48 * rereads
                     + 0.58 * wrong_count + 0.19 * hint_count + 0.24 * (difficulty - 1)
                     + 0.12 * (branch == 0) + rng.gauss(0, 0.45))
            requested = int(rng.random() < sigmoid(logit))
            rows.append({
                "oturum_id": session_id, "karar_no": decision_no,
                "bekleme_suresi_sn": wait_s, "karar_degistirme": changes,
                "tekrar_okuma": rereads, "onceki_yanlis": wrong_count,
                "onceki_ipucu": hint_count, "zorluk": difficulty,
                "dal_kodu": branch, "ipucu_istendi": requested, "kaynak": "sentetik",
            })
            # Toy simulator feedback only; it is not evidence about real learners.
            if branch == 0 and rng.random() < 0.42:
                wrong_count = min(5, wrong_count + 1)
            if requested:
                hint_count = min(5, hint_count + 1)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"{len(rows)} synthetic decision rows -> {OUT}")


if __name__ == "__main__":
    main()
