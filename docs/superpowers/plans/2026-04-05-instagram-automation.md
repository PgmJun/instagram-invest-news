# Instagram 자동화 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 매일 08:00 KST GitHub Actions에서 main.py를 실행해 카드뉴스 6장을 생성하고 Instagram 캐러셀로 자동 게시한다.

**Architecture:** GitHub Actions 스케줄 트리거 → main.py (이미지 생성) → GitHub Release Asset (공개 URL 확보) → Meta Graph API (캐러셀 게시 + 댓글 📈 + 대댓글 해시태그).

**Tech Stack:** Python 3.11, requests, Meta Graph API v19.0, GitHub REST API, GitHub Actions

---

## 파일 구조

| 파일 | 작업 | 역할 |
|------|------|------|
| `requirements.txt` | 수정 | `requests`, `feedparser` 추가 |
| `services/github_release.py` | 신규 | GitHub Release 생성 + Asset 업로드 → 공개 URL 반환 |
| `services/instagram.py` | 신규 | Meta Graph API 래퍼 (캐러셀, 댓글, 대댓글) |
| `main.py` | 수정 | GitHub Release + Instagram 업로드 단계 추가 |
| `.github/workflows/daily.yml` | 신규 | 매일 08:00 KST 스케줄 워크플로우 |
| `tests/test_github_release.py` | 신규 | github_release 유닛 테스트 |
| `tests/test_instagram.py` | 신규 | instagram 서비스 유닛 테스트 |

---

## Task 1: requirements.txt 업데이트

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: `requests`와 `feedparser` 추가**

```
anthropic
yfinance
python-dotenv
playwright
requests
feedparser
```

- [ ] **Step 2: 설치 확인**

```bash
pip install -r requirements.txt
```

Expected: 오류 없이 설치 완료

- [ ] **Step 3: 커밋**

```bash
git add requirements.txt
git commit -m "chore: add requests and feedparser to requirements"
```

---

## Task 2: `services/github_release.py` 구현 (TDD)

**Files:**
- Create: `services/github_release.py`
- Create: `tests/test_github_release.py`

- [ ] **Step 1: tests 디렉토리 생성**

```bash
mkdir -p tests
touch tests/__init__.py
```

- [ ] **Step 2: 실패하는 테스트 작성**

`tests/test_github_release.py`:

```python
import os
from unittest.mock import patch, MagicMock, mock_open
import pytest
from services.github_release import create_release_and_upload


@patch.dict(os.environ, {
    "GITHUB_TOKEN": "fake-token",
    "GITHUB_REPOSITORY": "owner/repo",
})
@patch("services.github_release.requests.post")
@patch("builtins.open", mock_open(read_data=b"png-bytes"))
def test_create_release_and_upload_returns_urls(mock_post):
    # Create release response
    release_response = MagicMock()
    release_response.json.return_value = {
        "id": 12345,
        "upload_url": "https://uploads.github.com/repos/owner/repo/releases/12345/assets{?name,label}",
    }
    release_response.raise_for_status = MagicMock()

    # Upload asset response
    asset_response = MagicMock()
    asset_response.json.return_value = {"id": 99}
    asset_response.raise_for_status = MagicMock()

    mock_post.side_effect = [release_response, asset_response]

    urls = create_release_and_upload(["output/card1_20260405_0800.png"])

    assert len(urls) == 1
    assert "card1_20260405_0800.png" in urls[0]
    assert urls[0].startswith("https://github.com/owner/repo/releases/download/daily-")


@patch.dict(os.environ, {
    "GITHUB_TOKEN": "fake-token",
    "GITHUB_REPOSITORY": "owner/repo",
})
@patch("services.github_release.requests.post")
@patch("builtins.open", mock_open(read_data=b"png-bytes"))
def test_create_release_and_upload_six_images(mock_post):
    release_response = MagicMock()
    release_response.json.return_value = {
        "id": 1,
        "upload_url": "https://uploads.github.com/repos/owner/repo/releases/1/assets{?name,label}",
    }
    release_response.raise_for_status = MagicMock()

    asset_response = MagicMock()
    asset_response.json.return_value = {"id": 1}
    asset_response.raise_for_status = MagicMock()

    mock_post.side_effect = [release_response] + [asset_response] * 6

    paths = [f"output/card{i}_20260405_0800.png" for i in range(1, 7)]
    urls = create_release_and_upload(paths)

    assert len(urls) == 6
    assert mock_post.call_count == 7  # 1 release + 6 assets
```

- [ ] **Step 3: 테스트가 실패하는지 확인**

```bash
python -m pytest tests/test_github_release.py -v
```

Expected: `ImportError: cannot import name 'create_release_and_upload'`

- [ ] **Step 4: `services/github_release.py` 구현**

```python
import os
import requests
from pathlib import Path
from datetime import datetime


def create_release_and_upload(image_paths: list[str]) -> list[str]:
    """GitHub Release를 생성하고 이미지를 Asset으로 업로드한다. 공개 URL 목록을 반환."""
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    tag = f"daily-{datetime.now().strftime('%Y-%m-%d')}"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    resp = requests.post(
        f"https://api.github.com/repos/{repo}/releases",
        headers=headers,
        json={
            "tag_name": tag,
            "name": f"Daily Market Brief {datetime.now().strftime('%Y-%m-%d')}",
            "draft": False,
            "prerelease": False,
        },
    )
    resp.raise_for_status()
    upload_url_template = resp.json()["upload_url"]

    urls = []
    for path in image_paths:
        filename = Path(path).name
        upload_url = upload_url_template.split("{")[0] + f"?name={filename}"

        with open(path, "rb") as f:
            upload_resp = requests.post(
                upload_url,
                headers={**headers, "Content-Type": "image/png"},
                data=f,
            )
            upload_resp.raise_for_status()

        urls.append(f"https://github.com/{repo}/releases/download/{tag}/{filename}")

    return urls
```

- [ ] **Step 5: 테스트 통과 확인**

```bash
python -m pytest tests/test_github_release.py -v
```

Expected: 2 passed

- [ ] **Step 6: 커밋**

```bash
git add services/github_release.py tests/test_github_release.py tests/__init__.py
git commit -m "feat: add GitHub Release asset uploader"
```

---

## Task 3: `services/instagram.py` 구현 (TDD)

**Files:**
- Create: `services/instagram.py`
- Create: `tests/test_instagram.py`

- [ ] **Step 1: 실패하는 테스트 작성**

`tests/test_instagram.py`:

```python
import os
from unittest.mock import patch, MagicMock
import pytest
from services.instagram import upload_carousel, post_comment, post_reply


ENV = {
    "INSTAGRAM_USER_ID": "123456789",
    "INSTAGRAM_ACCESS_TOKEN": "fake-access-token",
}


@patch.dict(os.environ, ENV)
@patch("services.instagram.requests.post")
@patch("services.instagram.time.sleep")
def test_upload_carousel_returns_media_id(mock_sleep, mock_post):
    # 6 image containers + 1 carousel container + 1 publish = 8 calls
    responses = []
    for i in range(6):
        r = MagicMock()
        r.json.return_value = {"id": f"container_{i}"}
        r.raise_for_status = MagicMock()
        responses.append(r)

    carousel_r = MagicMock()
    carousel_r.json.return_value = {"id": "carousel_999"}
    carousel_r.raise_for_status = MagicMock()
    responses.append(carousel_r)

    publish_r = MagicMock()
    publish_r.json.return_value = {"id": "media_777"}
    publish_r.raise_for_status = MagicMock()
    responses.append(publish_r)

    mock_post.side_effect = responses

    image_urls = [f"https://github.com/owner/repo/releases/download/daily-2026-04-05/card{i}.png" for i in range(1, 7)]
    media_id = upload_carousel(image_urls, "테스트 캡션")

    assert media_id == "media_777"
    assert mock_post.call_count == 8


@patch.dict(os.environ, ENV)
@patch("services.instagram.requests.post")
def test_post_comment_returns_comment_id(mock_post):
    r = MagicMock()
    r.json.return_value = {"id": "comment_111"}
    r.raise_for_status = MagicMock()
    mock_post.return_value = r

    comment_id = post_comment("media_777", "📈")

    assert comment_id == "comment_111"
    call_args = mock_post.call_args
    assert "message" in call_args.kwargs["params"]
    assert call_args.kwargs["params"]["message"] == "📈"


@patch.dict(os.environ, ENV)
@patch("services.instagram.requests.post")
def test_post_reply_returns_reply_id(mock_post):
    r = MagicMock()
    r.json.return_value = {"id": "reply_222"}
    r.raise_for_status = MagicMock()
    mock_post.return_value = r

    reply_id = post_reply("comment_111", "#주식 #재테크")

    assert reply_id == "reply_222"
    call_args = mock_post.call_args
    assert "#주식 #재테크" in call_args.kwargs["params"]["message"]
```

- [ ] **Step 2: 테스트가 실패하는지 확인**

```bash
python -m pytest tests/test_instagram.py -v
```

Expected: `ImportError: cannot import name 'upload_carousel'`

- [ ] **Step 3: `services/instagram.py` 구현**

```python
import os
import time
import requests


BASE_URL = "https://graph.facebook.com/v19.0"


def _post(endpoint: str, params: dict) -> dict:
    params = {**params, "access_token": os.environ["INSTAGRAM_ACCESS_TOKEN"]}
    resp = requests.post(f"{BASE_URL}/{endpoint}", params=params)
    resp.raise_for_status()
    return resp.json()


def upload_carousel(image_urls: list[str], caption: str) -> str:
    """캐러셀 게시물을 업로드하고 게시된 media ID를 반환."""
    user_id = os.environ["INSTAGRAM_USER_ID"]

    container_ids = []
    for url in image_urls:
        data = _post(f"{user_id}/media", {
            "image_url": url,
            "is_carousel_item": "true",
        })
        container_ids.append(data["id"])

    carousel = _post(f"{user_id}/media", {
        "media_type": "CAROUSEL",
        "children": ",".join(container_ids),
        "caption": caption,
    })

    time.sleep(5)

    published = _post(f"{user_id}/media_publish", {
        "creation_id": carousel["id"],
    })

    return published["id"]


def post_comment(media_id: str, text: str) -> str:
    """게시물에 댓글을 달고 comment ID를 반환."""
    data = _post(f"{media_id}/comments", {"message": text})
    return data["id"]


def post_reply(comment_id: str, text: str) -> str:
    """댓글에 대댓글을 달고 reply ID를 반환."""
    data = _post(f"{comment_id}/replies", {"message": text})
    return data["id"]
```

- [ ] **Step 4: 테스트 통과 확인**

```bash
python -m pytest tests/test_instagram.py -v
```

Expected: 3 passed

- [ ] **Step 5: 커밋**

```bash
git add services/instagram.py tests/test_instagram.py
git commit -m "feat: add Instagram Meta Graph API service"
```

---

## Task 4: `main.py` 수정

**Files:**
- Modify: `main.py`

- [ ] **Step 1: main.py 전체 교체**

```python
from services.market_data import get_market_data
from services.claude import generate_market_content
from generator.card_generator import generate_all_cards
from services.github_release import create_release_and_upload
from services.instagram import upload_carousel, post_comment, post_reply

HASHTAGS = (
    "#주식 #재테크 #코스피 #나스닥 #미국주식 #주식투자 "
    "#경제 #투자 #시장분석 #글로벌시장 #MarketBrief #오늘의주식"
)


def build_caption(result: dict) -> str:
    headline = result["analysis"]["headline"]
    action = result["cta"]["action"]
    return f"📊 {headline}\n\n{action}\n\n👉 매일 아침 자동 브리핑 받으려면 팔로우"


def main():
    print("📊 데이터 수집 중...")
    data = get_market_data()

    result = generate_market_content(data)

    print("🖼️ 카드 생성 중...")
    images = generate_all_cards(result)

    print("📤 GitHub Release 업로드 중...")
    image_urls = create_release_and_upload(images)

    print("📱 Instagram 업로드 중...")
    caption = build_caption(result)
    media_id = upload_carousel(image_urls, caption)

    comment_id = post_comment(media_id, "📈")
    post_reply(comment_id, HASHTAGS)

    print("✅ 완료!")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 전체 테스트 통과 확인**

```bash
python -m pytest tests/ -v
```

Expected: 5 passed

- [ ] **Step 3: 커밋**

```bash
git add main.py
git commit -m "feat: wire up GitHub Release and Instagram upload in main"
```

---

## Task 5: `.github/workflows/daily.yml` 생성

**Files:**
- Create: `.github/workflows/daily.yml`

- [ ] **Step 1: 디렉토리 생성**

```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: 워크플로우 파일 작성**

`.github/workflows/daily.yml`:

```yaml
name: Daily Market Brief

on:
  schedule:
    - cron: '0 23 * * *'  # 08:00 KST (UTC+9)
  workflow_dispatch:       # 수동 실행 (테스트용)

jobs:
  post:
    runs-on: ubuntu-latest
    permissions:
      contents: write  # Release 생성에 필요

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: pip install -r requirements.txt

      - name: Install Playwright browsers
        run: playwright install chromium --with-deps

      - name: Run main.py
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
          INSTAGRAM_ACCESS_TOKEN: ${{ secrets.INSTAGRAM_ACCESS_TOKEN }}
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_REPOSITORY: ${{ github.repository }}
        run: python main.py
```

- [ ] **Step 3: 커밋**

```bash
git add .github/workflows/daily.yml
git commit -m "ci: add daily GitHub Actions workflow for Instagram posting"
```

---

## Task 6: GitHub Secrets 설정

> 코드 작업 없음 — GitHub 레포 설정에서 직접 입력.

- [ ] **Step 1: GitHub 레포 → Settings → Secrets and variables → Actions → New repository secret**

| Secret 이름 | 값 찾는 방법 |
|------------|------------|
| `ANTHROPIC_API_KEY` | 기존 `.env` 파일에 있는 값 |
| `INSTAGRAM_USER_ID` | Meta for Developers → Instagram Graph API → 계정 ID |
| `INSTAGRAM_ACCESS_TOKEN` | Meta for Developers → Graph API Explorer → 장기 토큰 생성 (아래 참고) |

- [ ] **Step 2: Instagram 장기 액세스 토큰 발급 방법**

1. Meta for Developers (developers.facebook.com) → 앱 생성 (비즈니스 앱)
2. Instagram Graph API 제품 추가
3. Graph API Explorer → `instagram_basic`, `instagram_content_publish`, `pages_read_engagement` 권한 선택
4. 단기 토큰(1시간) 발급 후 장기 토큰(60일)으로 교환:

```bash
curl "https://graph.facebook.com/v19.0/oauth/access_token
  ?grant_type=fb_exchange_token
  &client_id={app-id}
  &client_secret={app-secret}
  &fb_exchange_token={short-lived-token}"
```

5. 반환된 `access_token` 값을 `INSTAGRAM_ACCESS_TOKEN` Secret에 저장

- [ ] **Step 3: workflow_dispatch로 수동 테스트 실행**

GitHub 레포 → Actions → Daily Market Brief → Run workflow → Run workflow 클릭

Expected: 워크플로우 성공, 인스타그램에 캐러셀 게시됨

---

## Self-Review

**스펙 커버리지 체크:**
- [x] GitHub Actions 매일 08:00 KST 스케줄 → Task 5
- [x] main.py 실행 → Task 4
- [x] GitHub Release Asset 업로드 → Task 2
- [x] Instagram 캐러셀 업로드 (6장) → Task 3
- [x] 캡션(본문) → Task 4 (`build_caption`)
- [x] 댓글 📈 → Task 3/4
- [x] 대댓글 해시태그 → Task 3/4
- [x] `requests`, `feedparser` 의존성 → Task 1

**타입/메서드 일관성:**
- `create_release_and_upload(image_paths: list[str]) -> list[str]` — Task 2 정의, Task 4에서 동일하게 사용
- `upload_carousel(image_urls: list[str], caption: str) -> str` — Task 3 정의, Task 4에서 동일하게 사용
- `post_comment(media_id: str, text: str) -> str` — Task 3 정의, Task 4에서 동일하게 사용
- `post_reply(comment_id: str, text: str) -> str` — Task 3 정의, Task 4에서 동일하게 사용
