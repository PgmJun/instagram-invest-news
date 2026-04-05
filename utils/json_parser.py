import json
import re


def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        pass

    text = re.sub(r"```json|```", "", text).strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return json.loads(match.group())

    raise ValueError("JSON 파싱 실패")
