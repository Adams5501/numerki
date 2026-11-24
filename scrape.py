#!/usr/bin/env python3
"""Pobiera szczęśliwe numerki ze strony ZS Nr 1 w Gorlicach i dopisuje je do data/numerki.json.

Strona pokazuje tylko jeden dzień (bez archiwum), dlatego historia powstaje przez
regularne uruchamianie tego skryptu. Tylko biblioteka standardowa Pythona.

Użycie:
    python scrape.py                 # pobiera ze strony
    python scrape.py --file x.html   # testowo, z pliku
"""
import argparse
import html
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

URL = "https://www.lukasiewicz.gorlice.pl"
DATA = Path(__file__).parent / "data" / "numerki.json"

MONTHS = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10,
    "listopada": 11, "grudnia": 12,
}


def to_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style).*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def parse(raw: str):
    """Zwraca (data_iso, [numerki]) albo rzuca ValueError."""
    text = to_text(raw)
    m = re.search(r"Szczęśliwe numerki(.{0,400})", text, re.I)
    if not m:
        raise ValueError("Nie znaleziono bloku 'Szczęśliwe numerki'")
    block = m.group(1)

    d = re.search(r"(\d{1,2})\s+(" + "|".join(MONTHS) + r")\s+(\d{4})", block, re.I)
    if not d:
        raise ValueError("Nie znaleziono daty przy numerkach")
    date_iso = f"{int(d.group(3)):04d}-{MONTHS[d.group(2).lower()]:02d}-{int(d.group(1)):02d}"

    after = block[d.end():]
    # Układ: "Numerek 1 <liczba> Numerek 2 <liczba>"
    nums = [int(x) for x in re.findall(r"Numerek\s+\d+\s+(\d{1,3})", after, re.I)]
    if not nums:
        raise ValueError("Nie znaleziono numerków po dacie")
    return date_iso, nums


def load():
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"updated": None, "entries": {}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", help="czytaj HTML/tekst z pliku zamiast ze strony")
    args = ap.parse_args()

    if args.file:
        raw = Path(args.file).read_text(encoding="utf-8")
    else:
        req = urllib.request.Request(URL, headers={"User-Agent": "numerki-bot/1.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            raw = r.read().decode("utf-8", errors="replace")

    try:
        date_iso, nums = parse(raw)
    except ValueError as e:
        print(f"BŁĄD: {e}", file=sys.stderr)
        sys.exit(1)

    data = load()
    old = data["entries"].get(date_iso)
    if old == nums:
        print(f"Bez zmian: {date_iso} -> {nums}")
        return
    data["entries"][date_iso] = nums
    data["entries"] = dict(sorted(data["entries"].items()))
    data["updated"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    # Kopia jako skrypt JS – dzięki temu strona działa też po otwarciu z dysku (file://)
    DATA.with_suffix(".js").write_text(
        "window.NUMERKI_DATA = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{'Zaktualizowano' if old else 'Dodano'}: {date_iso} -> {nums}")


if __name__ == "__main__":
    main()
