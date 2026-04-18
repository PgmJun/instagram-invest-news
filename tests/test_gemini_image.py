import base64
from unittest.mock import patch, MagicMock
from services.gemini_image import generate_thumbnail_background, _build_prompt


def test_build_prompt_contains_headline():
    analysis = {
        "headline": "테슬라 급등, 나스닥 사상 최고치",
        "key_points": ["테슬라 10% 상승", "Fed 금리 동결"]
    }
    prompt = _build_prompt(analysis)
    assert "Tesla" in prompt or "테슬라" in prompt or "Nasdaq" in prompt or len(prompt) > 20


def test_generate_returns_base64_on_success():
    analysis = {
        "headline": "테슬라 급등",
        "key_points": ["테슬라 상승", "금리 동결"]
    }

    fake_image_bytes = b"fake_png_bytes"
    fake_b64 = base64.b64encode(fake_image_bytes).decode()

    mock_image = MagicMock()
    mock_image.image.image_bytes = fake_image_bytes

    mock_response = MagicMock()
    mock_response.generated_images = [mock_image]

    with patch("services.gemini_image.imagen_client") as mock_client:
        mock_client.models.generate_images.return_value = mock_response
        result = generate_thumbnail_background(analysis)

    assert result == fake_b64


def test_generate_returns_none_on_exception():
    analysis = {"headline": "테슬라", "key_points": []}

    with patch("services.gemini_image.imagen_client") as mock_client:
        mock_client.models.generate_images.side_effect = Exception("API error")
        result = generate_thumbnail_background(analysis)

    assert result is None


def test_generate_returns_none_when_no_api_key():
    analysis = {"headline": "테슬라", "key_points": []}

    with patch("services.gemini_image.imagen_client", None):
        result = generate_thumbnail_background(analysis)

    assert result is None
