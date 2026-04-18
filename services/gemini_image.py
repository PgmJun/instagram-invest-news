import base64
import logging
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=1080&height=1350&nologo=true&model=flux"


def _build_prompt(analysis: dict, image_prompt: str = "") -> str:
    if image_prompt:
        return image_prompt

    headline = analysis.get("headline", "financial market")
    key_points = analysis.get("key_points", [])
    points_str = ", ".join(key_points[:3]) if key_points else ""

    return (
        f"Cinematic financial market background image: {headline}. "
        f"Key themes: {points_str}. "
        "Abstract stock market charts, data visualization, glowing light streaks, "
        "professional photography, no text, no letters, no numbers, ultra HD, 4K, dramatic lighting"
    )


def generate_thumbnail_background(analysis: dict, image_prompt: str = "") -> str | None:
    prompt = _build_prompt(analysis, image_prompt)
    encoded = urllib.parse.quote(prompt)
    url = POLLINATIONS_URL.format(prompt=encoded)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            image_bytes = resp.read()
        return base64.b64encode(image_bytes).decode()
    except Exception as e:
        logger.warning(f"AI 이미지 생성 실패 — 폴백 배경 사용: {e}")
        return None
