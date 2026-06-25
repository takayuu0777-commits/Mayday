import json
import os
import random


def load_tips():
    path = os.path.join(os.getcwd(), "data", "tips.json")

    if not os.path.exists(path):
        return []

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def today_tip():
    tips = load_tips()

    if not tips:
        return {
            "category": "💡 今日の発見",
            "text": "今日も小さな記録を残していきましょう。"
        }

    return random.choice(tips)