def generate_caption(analysis):

    headline = analysis["headline"]
    summary = analysis["market_summary"]
    tags = " ".join(analysis["hashtags"])

    return f"""
📊 {headline}

{summary}

👇 핵심 요약
✔️ 오늘 시장 흐름 체크
✔️ 내일 전망까지 확인

👉 매일 아침 자동 브리핑 받으려면 팔로우

{tags}
#주식 #재테크 #코스피 #나스닥
"""
