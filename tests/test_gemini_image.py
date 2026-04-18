import base64
from unittest.mock import patch, MagicMock
from services.gemini_image import generate_thumbnail_background, _build_prompt


def test_build_prompt_contains_headline():
    analysis = {
        "headline": "테슬라 급등, 나스닥 사상 최고치",
        "key_points": ["테슬라 10% 상승", "Fed 금리 동결"]
    }
    prompt = _build_prompt(analysis)
    assert "테슬라 급등" in prompt or "나스닥" in prompt
    assert len(prompt) > 20


def test_generate_returns_base64_on_success():
    analysis = {
        "headline": "테슬라 급등",
        "key_points": ["테슬라 상승", "금리 동결"]
    }

    fake_image_bytes = b"fake_png_bytes"
    fake_b64 = base64.b64encode(fake_image_bytes).decode()

    mock_resp = MagicMock()
    mock_resp.read.return_value = fake_image_bytes
    mock_resp.__enter__ = lambda s: s
    mock_resp.__exit__ = MagicMock(return_value=False)

    with patch("urllib.request.urlopen", return_value=mock_resp):
        result = generate_thumbnail_background(analysis)

    assert result == fake_b64


def test_generate_returns_none_on_exception():
    analysis = {"headline": "테슬라", "key_points": []}

    with patch("urllib.request.urlopen", side_effect=Exception("network error")):
        result = generate_thumbnail_background(analysis)

    assert result is None
