# AI 썸네일 생성 설계

Date: 2026-04-19

## 목표

현재 Python/HTML로 정적 그라디언트 배경으로 생성하는 인스타그램 썸네일(Card 1 Hook)을, Gemini API를 사용해 뉴스 내용 기반으로 매일 다른 AI 이미지를 배경으로 사용하도록 변경한다.

## 전체 흐름

```
기존: Claude 분석 → HTML 카드(그라디언트 배경) → Playwright PNG
변경: Claude 분석 → Gemini 배경 이미지 생성 → HTML 카드(AI 배경) → Playwright PNG
```

## 컴포넌트

### 신규: `services/gemini_image.py`

- `generate_thumbnail_background(analysis) -> str | None`
- `analysis`의 `headline`, `key_points`를 조합해 영어 프롬프트 자동 생성
- Gemini API (`imagen-3.0-generate-002` 또는 `gemini-2.0-flash-preview-image-generation`) 호출
- 생성된 이미지를 base64 문자열로 반환
- 실패 시 `None` 반환 (폴백 처리용)

**프롬프트 생성 예시:**
```
"Cinematic financial market background: {headline}.
Dark blue and teal color tones, abstract stock charts, data visualization,
professional photography style, no text, no letters, ultra HD, 4K"
```

### 변경: `generator/card_generator.py`

- `build_card1_hook(analysis, bg_image_b64=None)` — 파라미터 추가
- `bg_image_b64`가 있으면 `background-image: url('data:image/png;base64,...')` 사용
- `None`이면 기존 그라디언트 배경 유지 (폴백)

### 변경: `main.py`

- 카드 생성 전 `generate_thumbnail_background(result["analysis"])` 호출
- 반환값을 `generate_all_cards(result, bg_image_b64=...)` 로 전달

### 변경: `config/settings.py`

- `GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")` 추가

### 변경: `requirements.txt`

- `google-generativeai` 추가

### 변경: `.github/workflows/daily.yml`

- `GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}` 환경변수 추가

## 실패 처리

Gemini API 호출 실패 (네트워크 오류, 할당량 초과, 콘텐츠 필터 등) 시:
- 예외를 잡아 경고 로그 출력
- `None` 반환 → 기존 그라디언트 배경으로 폴백
- 서비스 중단 없음

## GitHub Actions Secret 추가 필요

`GEMINI_API_KEY`를 GitHub repo Settings → Secrets에 추가해야 함.
Google AI Studio (aistudio.google.com)에서 무료 API 키 발급 가능.

## 범위 외 (이번 작업 제외)

- Card 2~N은 기존 HTML 방식 유지
- Playwright 파이프라인 변경 없음
- Instagram 업로드 로직 변경 없음
