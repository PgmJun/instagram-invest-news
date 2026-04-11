from services.market_data import get_market_data
from services.claude import generate_market_content
from generator.card_generator import generate_all_cards
from services.github_pages import upload_images_to_pages
from services.instagram import upload_carousel, post_comment, post_reply

BASE_HASHTAGS = (
    "#주식 #재테크 #코스피 #나스닥 #미국주식 #주식투자 "
    "#경제 #투자 #시장분석 #글로벌시장 #MarketBrief #오늘의주식"
)


def build_hashtags(result: dict) -> str:
    dynamic = result.get("hashtags", [])
    extra = " ".join(dynamic)
    return f"{BASE_HASHTAGS} {extra}".strip()


def build_caption(result: dict) -> str:
    headline = result["analysis"]["headline"]
    action = result["cta"]["action"]
    return f"📊 {headline}\n\n{action}\n\n👉 매일 아침 자동 브리핑 받으려면 팔로우"


def main():
    print("📊 데이터 수집 중...")
    data = get_market_data()

    result = generate_market_content(data)

    print("🖼️ 카드 생성 중...")
    images = generate_all_cards(result)

    print("📤 GitHub Pages 업로드 중...")
    image_urls = upload_images_to_pages(images)

    print("📱 Instagram 업로드 중...")
    caption = build_caption(result)
    media_id = upload_carousel(image_urls, caption)

    comment_id = post_comment(media_id, "📈")
    post_reply(comment_id, build_hashtags(result))

    print("✅ 완료!")


if __name__ == "__main__":
    main()
