# Instagram 자동 업로드 자동화 설계

## 개요

매일 아침 8시(KST) GitHub Actions에서 `main.py`를 실행하여 주식 시장 카드뉴스 이미지 6장을 생성하고, Meta Graph API를 통해 Instagram 캐러셀로 자동 게시한다.

## 아키텍처

```
[GitHub Actions - 매일 08:00 KST / 23:00 UTC]
        ↓
1. main.py 실행
   → yfinance + RSS로 시장 데이터 수집
   → Claude Sonnet으로 분석 및 콘텐츠 생성
   → Playwright로 카드 6장 PNG 생성 (output/)
        ↓
2. GitHub Release 생성 (태그: daily-YYYY-MM-DD)
   → PNG 6장을 Release Asset으로 업로드
   → 공개 다운로드 URL 확보
        ↓
3. Instagram 업로드 (Meta Graph API)
   → 이미지 6개 개별 컨테이너 생성 (image_url 전달)
   → 캐러셀 컨테이너 생성 (caption 포함)
   → 캐러셀 게시 (media_publish)
   → 댓글 게시: 📈
   → 대댓글 게시: 해시태그
```

## 컴포넌트

### 기존 (변경 없음)
- `services/market_data.py` — yfinance + RSS 데이터 수집
- `services/claude.py` — Claude API로 콘텐츠 생성
- `generator/card_generator.py` — Playwright로 PNG 6장 생성
- `services/caption.py` — 캡션 + 해시태그 생성

### 신규
- `services/instagram.py` — Meta Graph API 래퍼
  - `upload_carousel(image_urls, caption)` → media_id
  - `post_comment(media_id, text)` → comment_id
  - `post_reply(comment_id, text)` → reply_id
- `.github/workflows/daily.yml` — 스케줄 워크플로우

### 수정
- `main.py` — Instagram 업로드 단계 추가 (기존 `print("완료:", images)` 교체)

## 데이터 흐름

1. `generate_all_cards(result)` → `["output/card1_YYYYMMDD_HHMM.png", ...]` (6개)
2. GitHub Release API → 각 PNG 업로드 → `["https://github.com/.../releases/download/daily-YYYY-MM-DD/card1_....png", ...]`
3. Meta API 순서:
   - `POST /{user_id}/media` × 6 (image_url 각각) → container_ids[]
   - `POST /{user_id}/media` (CAROUSEL, children=container_ids, caption=...) → carousel_id
   - `POST /{user_id}/media_publish` (creation_id=carousel_id) → published_media_id
   - `POST /{published_media_id}/comments` (text="📈") → comment_id
   - `POST /{comment_id}/replies` (text=hashtags) → reply_id

## 스케줄링

- GitHub Actions cron: `0 23 * * *` (UTC) = 08:00 KST
- 워크플로우 단계: Python 설치 → 의존성 설치 → Playwright 브라우저 설치 → main.py 실행

## 환경 변수 / Secrets

| 이름 | 출처 | 설명 |
|------|------|------|
| `ANTHROPIC_API_KEY` | GitHub Secrets | Claude API 키 |
| `INSTAGRAM_USER_ID` | GitHub Secrets | Instagram 비즈니스 계정 ID |
| `INSTAGRAM_ACCESS_TOKEN` | GitHub Secrets | Meta Graph API 장기 토큰 (60일마다 갱신) |
| `GITHUB_TOKEN` | Actions 자동 제공 | Release 생성 및 Asset 업로드용 |

## 에러 처리

- `main.py` 실패 시 Actions가 자동으로 실패 표시 (이메일 알림 설정 가능)
- Meta API 오류 시 예외를 raise하여 워크플로우 실패로 처리
- GitHub Release 업로드 실패 시 즉시 중단

## 제약 사항

- GitHub 레포는 public이어야 Release Asset URL이 인증 없이 접근 가능
- Meta Graph API Access Token은 60일마다 갱신 필요 (장기 토큰 사용)
- Instagram 캐러셀은 최대 10장까지 지원 (6장이므로 문제 없음)
- GitHub Actions 무료 티어: 월 2,000분 (하루 ~5분 실행 시 월 150분 사용 → 여유 있음)
