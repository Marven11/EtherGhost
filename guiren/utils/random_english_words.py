import json
import random
from pathlib import Path

DIR = Path(__file__).parent

with open(DIR / "eng_words_map.json", "r", encoding="utf-8") as f:
    jump_map = json.load(f)


def random_choose_from(words_weight: dict):
    p = random.randint(0, sum(words_weight.values()) - 1)
    for k, v in words_weight.items():
        if p >= v:
            p -= v
        if p <= 0:
            return k


def random_english_words():
    word = ""
    nxt = random_choose_from(jump_map[""])
    while nxt in jump_map and nxt != "":
        word += nxt
        nxt = random_choose_from(jump_map[nxt])
        if nxt not in jump_map or nxt == "":
            break
    return word
