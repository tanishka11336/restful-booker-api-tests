import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_data")


def load_json(file_name: str):
    with open(os.path.join(DATA_DIR, file_name), encoding="utf-8") as f:
        return json.load(f)
