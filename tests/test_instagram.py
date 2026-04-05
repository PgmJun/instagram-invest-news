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
