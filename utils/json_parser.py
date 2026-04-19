import json
import re


def safe_json_load(text):
    try:
        return json.loads(text)
    except:
        pass

    text = re.sub(r"```json|```", "", text).strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("JSON 파싱 실패")

    raw = match.group()
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # image_prompt 같은 문자열 필드 안의 이스케이프 안 된 따옴표 제거
        fixed = re.sub(
            r'("image_prompt"\s*:\s*)"(.*?)"(\s*[,}])',
            lambda m: m.group(1) + '"' + m.group(2).replace('"', "'") + '"' + m.group(3),
            raw,
            flags=re.DOTALL,
        )
        return json.loads(fixed)
