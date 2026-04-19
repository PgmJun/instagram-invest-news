from anthropic import Anthropic
from config.settings import settings
from utils.json_parser import safe_json_load
import json

client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

def generate_market_content(data):
    print("🤖 Claude 분석 중...")

    prompt = f"""너는 인스타그램 주식 카드뉴스 제작자다.

뉴스 기반으로 반드시 설명해라. 절대 추상적으로 말하지 마라.
JSON만 출력하고 다른 말 하지 마라. 코드블럭 절대 쓰지 마라.
key_points는 오늘 시장에서 중요한 포인트를 최소 3개, 최대 10개까지 뽑아라.
details는 key_points와 반드시 같은 개수로 만들어라. 각 detail은 해당 key_point를 상세히 설명한다.
hashtags는 오늘 콘텐츠 내용에 딱 맞는 한국어/영어 해시태그를 5~10개 뽑아라. # 포함해서 작성하고 기본 해시태그(주식, 재테크, 경제 등)는 제외하고 오늘 뉴스에 특화된 것만 넣어라.
image_prompt는 오늘 뉴스의 핵심 주제를 반영한 AI 이미지 생성용 영어 프롬프트다. 구체적인 사물/브랜드/장소를 포함해라. 스타일은 항상 cinematic, professional photography, no text, no letters, ultra HD, 4K, dramatic lighting 으로 끝내라.

중요: 모든 문자열 값 안에 줄바꿈이나 큰따옴표(")를 절대 넣지 마라.

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
  }},
  "hashtags": ["#...", "#...", "#..."],
  "image_prompt": "..."
}}

데이터:
{json.dumps(data, ensure_ascii=False, indent=2)}"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = response.content[0].text
    return safe_json_load(text)
