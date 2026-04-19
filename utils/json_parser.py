import json
import re


def _fix_json_strings(text):
    """JSON 문자열 값 안의 이스케이프 안 된 줄바꿈·따옴표를 수정한다."""
    result = []
    in_string = False
    escape_next = False

    for ch in text:
        if escape_next:
            result.append(ch)
            escape_next = False
        elif ch == '\\':
            result.append(ch)
            escape_next = True
        elif ch == '"':
            result.append(ch)
            in_string = not in_string
        elif in_string and ch == '\n':
            result.append('\\n')
        elif in_string and ch == '\r':
            pass  # 무시
        else:
            result.append(ch)

    return ''.join(result)


def safe_json_load(text):
    # 1차: 그대로 시도
    try:
        return json.loads(text)
    except Exception:
        pass

    # 코드블럭 제거
    text = re.sub(r"```json|```", "", text).strip()

    # 2차: 코드블럭 제거 후 시도
    try:
        return json.loads(text)
    except Exception:
        pass

    # JSON 객체 추출
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("JSON 파싱 실패: JSON 객체를 찾을 수 없음")

    raw = match.group()

    # 3차: 추출 후 시도
    try:
        return json.loads(raw)
    except Exception:
        pass

    # 4차: 줄바꿈·이스케이프 수정 후 시도
    fixed = _fix_json_strings(raw)
    try:
        return json.loads(fixed)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON 파싱 실패: {e}\n원본 앞 200자: {raw[:200]}")
