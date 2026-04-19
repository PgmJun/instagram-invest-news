import os
import time
import requests


BASE_URL = "https://graph.instagram.com/v25.0"


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


def share_post_to_story(media_id: str) -> str:
    """피드 게시물을 스토리로 공유하고 media ID를 반환."""
    user_id = os.environ["INSTAGRAM_USER_ID"]

    container = _post(f"{user_id}/media", {
        "source_media_id": media_id,
        "media_type": "STORIES",
    })

    time.sleep(3)

    published = _post(f"{user_id}/media_publish", {
        "creation_id": container["id"],
    })

    return published["id"]
