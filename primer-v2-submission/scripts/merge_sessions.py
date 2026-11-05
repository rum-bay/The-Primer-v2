"""Merge downloaded, consented real-session CSV files into the training dataset."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "data" / "oturumlar.csv"
EXPECTED = ["oturum_id", "karar_no", "bekleme_suresi_sn", "karar_degistirme", "tekrar_okuma",
            "onceki_yanlis", "onceki_ipucu", "zorluk", "dal_kodu", "ipucu_istendi", "kaynak"]

def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Kullanım: python scripts/merge_sessions.py <gercek-oturum.csv> [dosya2.csv ...]")
    combined = []
    for name in sys.argv[1:]:
        path = Path(name)
        with path.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames != EXPECTED:
                raise SystemExit(f"{path}: sütunlar SOZLUK.md ile uyuşmuyor")
            for row in reader:
                if row["kaynak"] != "gercek":
                    raise SystemExit(f"{path}: dışa aktarılan gerçek oturumlarda kaynak=gercek olmalı")
                combined.append(row)
    existing = []
    with DEST.open(newline="", encoding="utf-8-sig") as f:
        existing = list(csv.DictReader(f))
    ids = {r["oturum_id"] for r in existing}
    added = []
    for row in combined:
        if row["oturum_id"] not in ids:
            added.append(row)
            ids.add(row["oturum_id"])
    with DEST.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=EXPECTED)
        writer.writerows(added)
    print(f"{len(added)} gerçek karar satırı eklendi. Oturumlar toplamı: {len({r['oturum_id'] for r in existing + added})}")

if __name__ == "__main__":
    main()
