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
    release_response = MagicMock()
    release_response.json.return_value = {
        "id": 12345,
        "upload_url": "https://uploads.github.com/repos/owner/repo/releases/12345/assets{?name,label}",
    }
    release_response.raise_for_status = MagicMock()

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
