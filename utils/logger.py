import json
from datetime import datetime
from pathlib import Path

def save_log(data, folder="data"):
    Path(folder).mkdir(exist_ok=True)

    filename = datetime.now().strftime("%Y%m%d_%H%M.json")

    with open(f"{folder}/{filename}", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
