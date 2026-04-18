# AI Thumbnail Generation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Gemini API로 뉴스 내용 기반 AI 배경 이미지를 생성해 인스타그램 썸네일(Card 1)에 적용한다.

**Architecture:** Claude가 분석한 `headline`과 `key_points`로 영어 프롬프트를 자동 생성 → Gemini Imagen API 호출 → base64 이미지를 HTML `background-image`로 삽입 → 기존 Playwright 파이프라인으로 PNG 출력. Gemini 실패 시 기존 그라디언트 배경으로 폴백.

**Tech Stack:** `google-generativeai` SDK, Gemini `imagen-3.0-generate-002` 모델, Python base64, 기존 Playwright

---

## File Map

| 파일 | 역할 |
|------|------|
| `services/gemini_image.py` | **신규** — Gemini API 호출, 프롬프트 생성, base64 반환 |
| `generator/card_generator.py` | `build_card1_hook()`에 `bg_image_b64` 파라미터 추가 |
| `main.py` | Gemini 이미지 생성 호출 후 카드 생성에 전달 |
| `config/settings.py` | `GEMINI_API_KEY` 추가 |
| `requirements.txt` | `google-generativeai` 추가 |
| `.github/workflows/daily.yml` | `GEMINI_API_KEY` secret 환경변수 추가 |
| `tests/test_gemini_image.py` | **신규** — gemini_image 서비스 테스트 |

---

### Task 1: 설정 및 의존성 추가

**Files:**
- Modify: `config/settings.py`
- Modify: `requirements.txt`

- [ ] **Step 1: `requirements.txt`에 `google-generativeai` 추가**

```
anthropic
yfinance
python-dotenv
playwright
requests
feedparser
google-generativeai
```

- [ ] **Step 2: `config/settings.py`에 `GEMINI_API_KEY` 추가**

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    OUTPUT_DIR = "output"
    DATA_DIR = "data"

settings = Settings()
```

- [ ] **Step 3: 패키지 설치**

```bash
pip install google-generativeai
```

Expected: `Successfully installed google-generativeai-...`

- [ ] **Step 4: 커밋**

```bash
git add requirements.txt config/settings.py
git commit -m "feat: Gemini API 설정 추가"
```

---

### Task 2: `services/gemini_image.py` 구현

**Files:**
- Create: `services/gemini_image.py`
- Create: `tests/test_gemini_image.py`

- [ ] **Step 1: 테스트 파일 작성**

`tests/test_gemini_image.py`:

```python
import base64
from unittest.mock import patch, MagicMock
from services.gemini_image import generate_thumbnail_background, _build_prompt


def test_build_prompt_contains_headline():
    analysis = {
        "headline": "테슬라 급등, 나스닥 사상 최고치",
        "key_points": ["테슬라 10% 상승", "Fed 금리 동결"]
    }
    prompt = _build_prompt(analysis)
    assert "Tesla" in prompt or "테슬라" in prompt or "Nasdaq" in prompt or len(prompt) > 20


def test_generate_returns_base64_on_success():
    analysis = {
        "headline": "테슬라 급등",
        "key_points": ["테슬라 상승", "금리 동결"]
    }

    fake_image_bytes = b"fake_png_bytes"
    fake_b64 = base64.b64encode(fake_image_bytes).decode()

    mock_image = MagicMock()
    mock_image.image.image_bytes = fake_image_bytes

    mock_response = MagicMock()
    mock_response.generated_images = [mock_image]

    with patch("services.gemini_image.imagen_client") as mock_client:
        mock_client.models.generate_images.return_value = mock_response
        result = generate_thumbnail_background(analysis)

    assert result == fake_b64


def test_generate_returns_none_on_exception():
    analysis = {"headline": "테슬라", "key_points": []}

    with patch("services.gemini_image.imagen_client") as mock_client:
        mock_client.models.generate_images.side_effect = Exception("API error")
        result = generate_thumbnail_background(analysis)

    assert result is None


def test_generate_returns_none_when_no_api_key():
    analysis = {"headline": "테슬라", "key_points": []}

    with patch("services.gemini_image.imagen_client", None):
        result = generate_thumbnail_background(analysis)

    assert result is None
```

- [ ] **Step 2: 테스트 실행해서 실패 확인**

```bash
pytest tests/test_gemini_image.py -v
```

Expected: `ImportError` 또는 `ModuleNotFoundError` (아직 구현 없음)

- [ ] **Step 3: `services/gemini_image.py` 구현**

```python
import base64
import logging
from google import genai
from config.settings import settings

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    imagen_client = genai.Client(api_key=settings.GEMINI_API_KEY)
else:
    imagen_client = None
    logger.warning("GEMINI_API_KEY 없음 — AI 썸네일 비활성화")


def _build_prompt(analysis: dict) -> str:
    headline = analysis.get("headline", "financial market")
    key_points = analysis.get("key_points", [])
    points_str = ", ".join(key_points[:3]) if key_points else ""

    return (
        f"Cinematic financial market background image: {headline}. "
        f"Key themes: {points_str}. "
        "Dark navy blue and teal color palette, abstract stock market charts, "
        "data visualization, glowing light streaks, professional photography, "
        "no text, no letters, no numbers, ultra HD, 4K, dramatic lighting"
    )


def generate_thumbnail_background(analysis: dict) -> str | None:
    if imagen_client is None:
        logger.warning("Gemini 클라이언트 없음 — 폴백 배경 사용")
        return None

    prompt = _build_prompt(analysis)

    try:
        response = imagen_client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config={"number_of_images": 1, "aspect_ratio": "4:5"},
        )
        image_bytes = response.generated_images[0].image.image_bytes
        return base64.b64encode(image_bytes).decode()
    except Exception as e:
        logger.warning(f"Gemini 이미지 생성 실패 — 폴백 배경 사용: {e}")
        return None
```

- [ ] **Step 4: 테스트 실행해서 통과 확인**

```bash
pytest tests/test_gemini_image.py -v
```

Expected:
```
tests/test_gemini_image.py::test_build_prompt_contains_headline PASSED
tests/test_gemini_image.py::test_generate_returns_base64_on_success PASSED
tests/test_gemini_image.py::test_generate_returns_none_on_exception PASSED
tests/test_gemini_image.py::test_generate_returns_none_when_no_api_key PASSED
4 passed
```

- [ ] **Step 5: 커밋**

```bash
git add services/gemini_image.py tests/test_gemini_image.py
git commit -m "feat: Gemini 썸네일 배경 이미지 생성 서비스 추가"
```

---

### Task 3: `build_card1_hook()`에 AI 배경 적용

**Files:**
- Modify: `generator/card_generator.py:47-139`

- [ ] **Step 1: `build_card1_hook` 시그니처 및 배경 로직 수정**

`generator/card_generator.py`의 `build_card1_hook` 함수를 다음으로 교체:

```python
def build_card1_hook(analysis, bg_image_b64=None):
    headline = analysis.get("headline", "")
    subtext  = analysis.get("subtext", "오늘의 글로벌 시장 핵심 요약")

    if bg_image_b64:
        background_style = (
            f"background-image: url('data:image/jpeg;base64,{bg_image_b64}');"
            "background-size: cover; background-position: center;"
        )
        overlay_style = (
            "position:absolute; inset:0;"
            "background: linear-gradient(160deg, rgba(6,13,31,0.75) 0%, rgba(13,31,60,0.65) 50%, rgba(9,20,40,0.75) 100%);"
        )
    else:
        background_style = "background: linear-gradient(160deg, #060D1F 0%, #0D1F3C 50%, #091428 100%);"
        overlay_style = ""

    overlay_div = f'<div style="{overlay_style}"></div>' if overlay_style else ""

    return html_doc(f"""
<div style="
    width:1080px; height:1350px;
    {background_style}
    display:flex; flex-direction:column;
    justify-content:space-between;
    padding: 80px 72px;
    position:relative;
    overflow:hidden;
">
    {overlay_div}
    <!-- 배경 장식 원 -->
    <div style="
        position:absolute; top:-120px; right:-120px;
        width:560px; height:560px; border-radius:50%;
        background:radial-gradient(circle, rgba(0,212,170,0.15) 0%, transparent 70%);
    "></div>
    <div style="
        position:absolute; bottom:-80px; left:-80px;
        width:400px; height:400px; border-radius:50%;
        background:radial-gradient(circle, rgba(255,107,53,0.12) 0%, transparent 70%);
    "></div>
    <!-- 대각선 라인 장식 -->
    <div style="
        position:absolute; top:0; right:180px;
        width:2px; height:100%;
        background:linear-gradient(to bottom, transparent, rgba(0,212,170,0.2), transparent);
    "></div>

    <!-- 상단: 브랜드 -->
    <div style="display:flex; align-items:center; gap:16px; position:relative; z-index:1;">
        <div style="
            width:52px; height:52px; border-radius:14px;
            background:linear-gradient(135deg,#00D4AA,#00A884);
            display:flex; align-items:center; justify-content:center;
            font-size:24px;
        ">📈</div>
        <div>
            <div style="color:#00D4AA; font-size:18px; font-weight:700; letter-spacing:2px;">MARKET BRIEF</div>
            <div style="color:rgba(255,255,255,0.45); font-size:13px; letter-spacing:1px;">TODAY'S KEY INSIGHTS</div>
        </div>
    </div>

    <!-- 중앙: 메인 헤드라인 -->
    <div style="position:relative; z-index:1; flex:1; display:flex; flex-direction:column; justify-content:center; padding:60px 0;">
        <div style="
            display:inline-block; width:fit-content;
            background:rgba(0,212,170,0.15); border:1px solid rgba(0,212,170,0.3);
            border-radius:100px; padding:10px 24px; margin-bottom:40px;
            color:#00D4AA; font-size:16px; font-weight:500; letter-spacing:1px;
        ">🔥 오늘의 핵심</div>

        <div style="
            font-size:68px; font-weight:900; line-height:1.15;
            color:#FFFFFF; letter-spacing:-1px;
            word-break:keep-all;
        ">{headline}</div>

        <div style="
            margin-top:40px;
            width:80px; height:4px;
            background:linear-gradient(to right, #00D4AA, transparent);
            border-radius:2px;
        "></div>

        <div style="
            margin-top:32px; font-size:26px; font-weight:400;
            color:rgba(255,255,255,0.6); line-height:1.6; word-break:keep-all;
        ">{subtext}</div>
    </div>

    <!-- 하단: 날짜 및 스와이프 안내 -->
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        position:relative; z-index:1;
        border-top:1px solid rgba(255,255,255,0.08); padding-top:36px;
    ">
        <div style="color:rgba(255,255,255,0.75); font-size:26px; font-weight:700;">
            {_date_str()}
        </div>
        <div style="
            display:flex; align-items:center; gap:10px;
            color:rgba(255,255,255,0.5); font-size:15px;
        ">
            <span>스와이프해서 확인</span>
            <span style="color:#00D4AA; font-size:20px;">→</span>
        </div>
    </div>
</div>""")
```

- [ ] **Step 2: `generate_all_cards`에 `bg_image_b64` 파라미터 추가**

`generator/card_generator.py`의 `generate_all_cards` 함수 시그니처와 내부 Card 1 생성 부분 수정:

```python
def generate_all_cards(result, output_dir="output", bg_image_b64=None):
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    base = Path(output_dir)

    analysis = result.get("analysis", {})
    details  = result.get("details", [])
    cta      = result.get("cta", {})

    total_cards = 2 + len(details) + 1

    cards = [build_card1_hook(analysis, bg_image_b64=bg_image_b64), build_card2_summary(analysis, total_cards)]
    for i, detail in enumerate(details):
        cards.append(build_detail_card(detail, card_num=3 + i, total_cards=total_cards, detail_idx=i))
    cards.append(build_cta_card(cta, total_cards))

    from playwright.sync_api import sync_playwright

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for i, html in enumerate(cards, 1):
            file = base / f"card{i}_{ts}.png"

            page = browser.new_page(viewport={"width": 1080, "height": 1350})
            page.set_content(html)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(file), full_page=False)
            results.append(str(file))

        browser.close()

    return results
```

- [ ] **Step 3: 커밋**

```bash
git add generator/card_generator.py
git commit -m "feat: Card 1에 AI 배경 이미지 파라미터 추가"
```

---

### Task 4: `main.py` 연결

**Files:**
- Modify: `main.py`

- [ ] **Step 1: `main.py` 수정**

`main.py` 전체를 다음으로 교체:

```python
from services.market_data import get_market_data
from services.claude import generate_market_content
from services.gemini_image import generate_thumbnail_background
from generator.card_generator import generate_all_cards
from services.github_pages import upload_images_to_pages
from services.instagram import upload_carousel, post_comment, post_reply

BASE_HASHTAGS = (
    "#주식 #재테크 #코스피 #나스닥 #미국주식 #주식투자 "
    "#경제 #투자 #시장분석 #글로벌시장 #MarketBrief #오늘의주식"
)


def build_hashtags(result: dict) -> str:
    dynamic = result.get("hashtags", [])
    extra = " ".join(dynamic)
    return f"{BASE_HASHTAGS} {extra}".strip()


def build_caption(result: dict) -> str:
    headline = result["analysis"]["headline"]
    action = result["cta"]["action"]
    return f"📊 {headline}\n\n{action}\n\n👉 매일 아침 자동 브리핑 받으려면 팔로우"


def main():
    print("📊 데이터 수집 중...")
    data = get_market_data()

    result = generate_market_content(data)

    print("🎨 AI 썸네일 배경 생성 중...")
    bg_image_b64 = generate_thumbnail_background(result["analysis"])
    if bg_image_b64:
        print("✅ AI 배경 이미지 생성 완료")
    else:
        print("⚠️ AI 배경 생성 실패 — 기본 배경 사용")

    print("🖼️ 카드 생성 중...")
    images = generate_all_cards(result, bg_image_b64=bg_image_b64)

    print("📤 GitHub Pages 업로드 중...")
    image_urls = upload_images_to_pages(images)

    print("📱 Instagram 업로드 중...")
    caption = build_caption(result)
    media_id = upload_carousel(image_urls, caption)

    comment_id = post_comment(media_id, "📈")
    post_reply(comment_id, build_hashtags(result))

    print("✅ 완료!")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 커밋**

```bash
git add main.py
git commit -m "feat: main.py에 Gemini 썸네일 생성 연결"
```

---

### Task 5: GitHub Actions에 GEMINI_API_KEY 추가

**Files:**
- Modify: `.github/workflows/daily.yml`

- [ ] **Step 1: `daily.yml` 수정**

`Run main.py` 스텝의 `env` 블록에 추가:

```yaml
      - name: Run main.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: python main.py
```

- [ ] **Step 2: 커밋**

```bash
git add .github/workflows/daily.yml
git commit -m "feat: GitHub Actions에 GEMINI_API_KEY secret 추가"
```

- [ ] **Step 3: GitHub 레포 → Settings → Secrets → Actions에 `GEMINI_API_KEY` 값 등록**

Google AI Studio (aistudio.google.com) → "Get API key" → 키 복사 후 GitHub secret에 등록.

---

### Task 6: 전체 테스트 실행 및 검증

- [ ] **Step 1: 전체 테스트 실행**

```bash
pytest tests/ -v
```

Expected: 모든 테스트 PASS

- [ ] **Step 2: 로컬 `.env`에 `GEMINI_API_KEY` 추가 후 수동 실행 테스트**

`.env` 파일:
```
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIza...
```

```bash
python -c "
from services.gemini_image import generate_thumbnail_background
result = generate_thumbnail_background({'headline': '테슬라 급등', 'key_points': ['테슬라 10% 상승']})
print('성공' if result else '실패 (폴백 동작)')
print(f'base64 길이: {len(result) if result else 0}')
"
```

Expected: `성공`, `base64 길이: (큰 숫자)`

- [ ] **Step 3: 최종 커밋 및 푸시**

```bash
git push origin main
```
