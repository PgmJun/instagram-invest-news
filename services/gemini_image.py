import base64
import logging
from google import genai
from config.settings import settings

logger = logging.getLogger(__name__)

if settings.GEMINI_API_KEY:
    imagen_client = genai.Client(api_key=settings.GEMINI_API_KEY)
else:
    imagen_client = None
    logger.warning("GEMINI_API_KEY 없음 — AI 썸네일 비활성화")


def _build_prompt(analysis: dict) -> str:
    headline = analysis.get("headline", "financial market")
    key_points = analysis.get("key_points", [])
    points_str = ", ".join(key_points[:3]) if key_points else ""

    return (
        f"Cinematic financial market background image: {headline}. "
        f"Key themes: {points_str}. "
        "Dark navy blue and teal color palette, abstract stock market charts, "
        "data visualization, glowing light streaks, professional photography, "
        "no text, no letters, no numbers, ultra HD, 4K, dramatic lighting"
    )


def generate_thumbnail_background(analysis: dict) -> str | None:
    if imagen_client is None:
        logger.warning("Gemini 클라이언트 없음 — 폴백 배경 사용")
        return None

    prompt = _build_prompt(analysis)

    try:
        response = imagen_client.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config={"number_of_images": 1, "aspect_ratio": "4:5"},
        )
        image_bytes = response.generated_images[0].image.image_bytes
        return base64.b64encode(image_bytes).decode()
    except Exception as e:
        logger.warning(f"Gemini 이미지 생성 실패 — 폴백 배경 사용: {e}")
        return None
