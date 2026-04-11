# GitHub Pages 이미지 호스팅 구현 계획

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 이미지 호스팅을 GitHub Releases에서 GitHub Pages로 교체해 안정적인 영구 공개 URL을 Instagram API에 제공한다.

**Architecture:** `services/github_pages.py`를 신규 생성해 gh-pages 브랜치에 GitHub Contents API로 이미지를 업로드한다. 브랜치 초기화, 구 이미지 자동 삭제, 업로드 후 CDN 전파 대기를 순서대로 수행하고 Pages URL 목록을 반환한다. `main.py`의 import만 교체하면 연결된다.

**Tech Stack:** Python 3.11, requests, GitHub REST API v2022-11-28

---

## 파일 구조

| 상태 | 경로 | 역할 |
|------|------|------|
| 신규 | `services/github_pages.py` | gh-pages 브랜치 관리 + 이미지 업로드 |
| 수정 | `main.py` | import를 github_pages로 교체 |
| 유지 | `services/github_release.py` | 삭제 없이 그대로 유지 |
| 유지 | `.github/workflows/daily.yml` | 변경 없음 |

---

### Task 1: `services/github_pages.py` 생성

**Files:**
- Create: `services/github_pages.py`

- [ ] **Step 1: 파일 생성 — 헬퍼 및 브랜치 초기화**

```python
import os
import base64
import time
import requests
from pathlib import Path
from datetime import datetime


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _ensure_gh_pages_branch(repo: str) -> None:
    """gh-pages 브랜치가 없으면 orphan 브랜치로 생성하고 GitHub Pages를 활성화한다."""
    h = _headers()

    # 브랜치 존재 확인
    resp = requests.get(f"https://api.github.com/repos/{repo}/branches/gh-pages", headers=h)
    if resp.status_code == 200:
        return

    # 빈 트리 생성
    tree = requests.post(
        f"https://api.github.com/repos/{repo}/git/trees",
        headers=h,
        json={"tree": []},
    )
    tree.raise_for_status()

    # orphan 커밋 생성
    commit = requests.post(
        f"https://api.github.com/repos/{repo}/git/commits",
        headers=h,
        json={"message": "Initialize gh-pages", "tree": tree.json()["sha"], "parents": []},
    )
    commit.raise_for_status()

    # 브랜치 ref 생성
    ref = requests.post(
        f"https://api.github.com/repos/{repo}/git/refs",
        headers=h,
        json={"ref": "refs/heads/gh-pages", "sha": commit.json()["sha"]},
    )
    ref.raise_for_status()

    # GitHub Pages 활성화 (이미 활성화된 경우 422 무시)
    pages = requests.post(
        f"https://api.github.com/repos/{repo}/pages",
        headers=h,
        json={"source": {"branch": "gh-pages", "path": "/"}},
    )
    if pages.status_code not in (201, 409, 422):
        pages.raise_for_status()
```

- [ ] **Step 2: 구 이미지 정리 함수 추가**

```python
def _cleanup_old_images(repo: str, today_prefix: str) -> None:
    """오늘 날짜로 시작하지 않는 images/* 폴더의 파일을 모두 삭제한다."""
    h = _headers()

    resp = requests.get(
        f"https://api.github.com/repos/{repo}/contents/images",
        headers=h,
        params={"ref": "gh-pages"},
    )
    # images/ 폴더가 아직 없으면 스킵
    if resp.status_code == 404:
        return
    resp.raise_for_status()

    for folder in resp.json():
        if folder["type"] != "dir":
            continue
        if folder["name"].startswith(today_prefix):
            continue

        # 폴더 내 파일 조회
        files_resp = requests.get(folder["url"], headers=h, params={"ref": "gh-pages"})
        files_resp.raise_for_status()

        for f in files_resp.json():
            del_resp = requests.delete(
                f"https://api.github.com/repos/{repo}/contents/{f['path']}",
                headers=h,
                json={"message": f"Remove old image {f['name']}", "sha": f["sha"], "branch": "gh-pages"},
            )
            del_resp.raise_for_status()
```

- [ ] **Step 3: 이미지 업로드 함수 추가**

```python
def _upload_image(repo: str, file_path: str, folder: str) -> str:
    """이미지를 gh-pages 브랜치에 업로드하고 GitHub Pages URL을 반환한다."""
    h = _headers()
    filename = Path(file_path).name
    content_path = f"images/{folder}/{filename}"

    with open(file_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    resp = requests.put(
        f"https://api.github.com/repos/{repo}/contents/{content_path}",
        headers=h,
        json={
            "message": f"Add {filename}",
            "content": encoded,
            "branch": "gh-pages",
        },
    )
    resp.raise_for_status()

    owner, repo_name = repo.split("/")
    return f"https://{owner}.github.io/{repo_name}/{content_path}"
```

- [ ] **Step 4: 공개 인터페이스 함수 추가**

```python
def upload_images_to_pages(image_paths: list[str]) -> list[str]:
    """이미지를 gh-pages 브랜치에 업로드하고 GitHub Pages URL 목록을 반환한다."""
    repo = os.environ["GITHUB_REPOSITORY"]
    folder = datetime.now().strftime("%Y-%m-%d-%H%M")
    today_prefix = datetime.now().strftime("%Y-%m-%d")

    _ensure_gh_pages_branch(repo)
    _cleanup_old_images(repo, today_prefix)

    urls = [_upload_image(repo, path, folder) for path in image_paths]

    # GitHub Pages CDN 전파 대기
    time.sleep(60)

    return urls
```

- [ ] **Step 5: 커밋**

```bash
git add services/github_pages.py
git commit -m "feat: GitHub Pages 이미지 호스팅 서비스 추가"
```

---

### Task 2: `main.py` import 교체

**Files:**
- Modify: `main.py`

- [ ] **Step 1: import 교체**

`main.py` 상단의

```python
from services.github_release import create_release_and_upload
```

를

```python
from services.github_pages import upload_images_to_pages
```

로 교체한다.

- [ ] **Step 2: 호출부 교체**

```python
# 변경 전
image_urls = create_release_and_upload(images)

# 변경 후
image_urls = upload_images_to_pages(images)
```

- [ ] **Step 3: 커밋**

```bash
git add main.py
git commit -m "feat: 이미지 호스팅을 GitHub Pages로 전환"
```

---

### Task 3: 푸시 및 동작 확인

- [ ] **Step 1: 푸시**

```bash
git push origin main
```

- [ ] **Step 2: GitHub Actions에서 workflow_dispatch로 수동 실행**

GitHub 레포 → Actions → Daily Market Brief → Run workflow

- [ ] **Step 3: 성공 확인 체크리스트**

1. Actions 로그에서 에러 없이 완료 확인
2. `gh-pages` 브랜치에 `images/YYYY-MM-DD-HHMM/` 폴더와 이미지 파일 생성 확인
3. `https://pgmjun.github.io/instagram-invest-news/images/.../card1_....png` 브라우저에서 접근 확인
4. Instagram에 카드뉴스 정상 게시 확인
