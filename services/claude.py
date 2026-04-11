from anthropic import Anthropic
from config.settings import settings
from utils.json_parser import safe_json_load
import json

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def generate_market_content(data):
    print("🤖 Claude 분석 중...")

    prompt = f"""
너는 인스타그램 주식 카드뉴스 제작자다.

뉴스 기반으로 반드시 설명해라.
절대 추상적으로 말하지 마라.
JSON만 출력하고 다른 말 하지 마라.
코드블럭 절대 쓰지 마라.
key_points는 오늘 시장에서 중요한 포인트를 최소 3개, 최대 10개까지 뽑아라.
details는 key_points와 반드시 같은 개수로 만들어라. 각 detail은 해당 key_point를 상세히 설명한다.

형식:

{{
  "analysis": {{
    "headline": "...",
    "key_points": ["...", "...", "..."]
  }},
  "details": [
    {{
      "title": "...",
      "summary": "...",
      "bullets": ["...", "...", "..."]
    }}
  ],
  "cta": {{
    "summary": "...",
    "action": "..."
  }}
}}

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text

    return safe_json_load(text)
