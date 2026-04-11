import os
import requests
from pathlib import Path
from datetime import datetime


def create_release_and_upload(image_paths: list[str]) -> list[str]:
    """GitHub Release를 생성하고 이미지를 Asset으로 업로드한다. 공개 URL 목록을 반환."""
    token = os.environ["GITHUB_TOKEN"]
    repo = os.environ["GITHUB_REPOSITORY"]
    tag = f"daily-{datetime.now().strftime('%Y-%m-%d-%H%M')}"

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

        github_url = f"https://github.com/{repo}/releases/download/{tag}/{filename}"
        direct = requests.get(github_url, allow_redirects=True, stream=True)
        direct.close()
        urls.append(direct.url)

    return urls
