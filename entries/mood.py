import json 
import re
from pathlib import Path

from entries.colloquial_lexicon import POSITIVE_CATEGORIES, NEGATIVE_CATEGORIES

LEXICON_PATH = Path(__file__).parent /"data"/"lexicon.json"

def _flatten(categories: dict) -> set:
    words = set()
    for word_set in categories.values():
        words |= word_set
    return words

def _load_lexicon():
    with LEXICON_PATH.open(encoding="utf-8") as f:
        data = json.load(f)
    positive = set(data["positive"]) | _flatten(POSITIVE_CATEGORIES)
    negative = set(data["negative"]) | _flatten(NEGATIVE_CATEGORIES)
    return positive, negative

POSITIVE_WORDS, NEGATIVE_WORDS = _load_lexicon()

def analyze_mood(text: str) -> float:
    if not text:
        return 0.0

    normalized = text.lower()
    tokens = re.findall(r"[\w\u0600-\u06ff]+", normalized)

    positive_count = sum(1 for t in tokens if t in POSITIVE_WORDS)
    negative_count = sum(1 for t in tokens if t in NEGATIVE_WORDS)

    total = positive_count + negative_count
    if total == 0.0:
        return 0.0

    return (positive_count - negative_count) / total