import json
import openpyxl
from pathlib import Path

SOURCE = Path("data/PerSentDataset.xlsx")
OUTPUT = Path("entries/data/lexicon.json")
POSITIVE_THRESHOLD = 0.3
NEGATIVE_THRESHOLD = -0.3
def build():
    wb = openpyxl.load_workbook(SOURCE, read_only=True)
    ws = wb["Dataset"]

    positive = set()
    negative = set()

    for word, pos, polarity in ws.iter_rows(min_row=2, values_only=True):
        if word is None or polarity is None:
            continue
        word = str(word).strip()
        if not word:
            continue
        score = float(polarity)
        if score >= POSITIVE_THRESHOLD:
            positive.add(word)
        elif score <= NEGATIVE_THRESHOLD:
            negative.add(word)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(
            {"positive": sorted(positive), "negative": sorted(negative)},
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"positive: {len(positive)}")
    print(f"negative {len(negative)}")
    print(f"written to {OUTPUT}")

if __name__ == "__main__":
    build()