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

    # GitHub Pages 활성화 (이미 활성화된 경우 409/422 무시)
    pages = requests.post(
        f"https://api.github.com/repos/{repo}/pages",
        headers=h,
        json={"source": {"branch": "gh-pages", "path": "/"}},
    )
    if pages.status_code not in (201, 409, 422):
        pages.raise_for_status()


def _cleanup_old_images(repo: str, today_prefix: str) -> None:
    """오늘 날짜로 시작하지 않는 images/* 폴더의 파일을 모두 삭제한다."""
    h = _headers()

    resp = requests.get(
        f"https://api.github.com/repos/{repo}/contents/images",
        headers=h,
        params={"ref": "gh-pages"},
    )
    if resp.status_code == 404:
        return
    resp.raise_for_status()

    for folder in resp.json():
        if folder["type"] != "dir":
            continue
        if folder["name"].startswith(today_prefix):
            continue

        files_resp = requests.get(folder["url"], headers=h, params={"ref": "gh-pages"})
        files_resp.raise_for_status()

        for f in files_resp.json():
            del_resp = requests.delete(
                f"https://api.github.com/repos/{repo}/contents/{f['path']}",
                headers=h,
                json={"message": f"Remove old image {f['name']}", "sha": f["sha"], "branch": "gh-pages"},
            )
            del_resp.raise_for_status()


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
