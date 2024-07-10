import json
import random
from uuid import uuid4
from pathlib import Path

DIR = Path(__file__).parent

with open(DIR / "eng_words_map.json", "r", encoding="utf-8") as f:
    eng_jump_map = json.load(f)

with open(DIR / "phone_5.json", "r", encoding="utf-8") as f:
    phone_5 = json.load(f)


def random_choose_from(words_weight: dict) -> str:
    p = random.randint(0, sum(words_weight.values()) - 1)
    for k, v in words_weight.items():
        p -= v
        if p <= 0:
            return k
    assert False

def random_english_words():
    word = ""
    nxt = random_choose_from(eng_jump_map[""])
    while nxt in eng_jump_map and nxt != "":
        word += nxt
        nxt = random_choose_from(eng_jump_map[nxt])
        if nxt not in eng_jump_map or nxt == "":
            break
    return word


def random_phone_number():
    isp = random_choose_from(
        {
            isp: sum(count for _, count in regions.items())
            for isp, regions in phone_5.items()
        }
    )
    region = random_choose_from(phone_5[isp])
    return isp + region + str(random.randint(1000000, 9999999))

def random_data():
    p = random.randint(1, 100)
    if p < 50:
        return random_english_words()
    if p < 55:
        return str(uuid4())
    return random_phone_number()
