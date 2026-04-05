from pathlib import Path
from datetime import datetime
import os


FONT_LINK = '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap" rel="stylesheet">'

BASE_STYLE = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        width: 1080px;
        height: 1440px;
        font-family: 'Noto Sans KR', sans-serif;
        overflow: hidden;
    }
"""


def html_doc(body_content, extra_style=""):
    return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    {FONT_LINK}
    <style>
        {BASE_STYLE}
        {extra_style}
    </style>
</head>
<body>
    {body_content}
</body>
</html>"""


# ── Card 1: Hook ──────────────────────────────────────────────────────────────
def build_card1_hook(analysis):
    headline = analysis.get("headline", "")
    subtext  = analysis.get("subtext", "오늘의 글로벌 시장 핵심 요약")

    return html_doc(f"""
<div style="
    width:1080px; height:1440px;
    background: linear-gradient(160deg, #060D1F 0%, #0D1F3C 50%, #091428 100%);
    display:flex; flex-direction:column;
    justify-content:space-between;
    padding: 80px 72px;
    position:relative;
    overflow:hidden;
">
    <!-- 배경 장식 원 -->
    <div style="
        position:absolute; top:-120px; right:-120px;
        width:560px; height:560px; border-radius:50%;
        background:radial-gradient(circle, rgba(0,212,170,0.15) 0%, transparent 70%);
    "></div>
    <div style="
        position:absolute; bottom:-80px; left:-80px;
        width:400px; height:400px; border-radius:50%;
        background:radial-gradient(circle, rgba(255,107,53,0.12) 0%, transparent 70%);
    "></div>
    <!-- 대각선 라인 장식 -->
    <div style="
        position:absolute; top:0; right:180px;
        width:2px; height:100%;
        background:linear-gradient(to bottom, transparent, rgba(0,212,170,0.2), transparent);
    "></div>

    <!-- 상단: 브랜드 -->
    <div style="display:flex; align-items:center; gap:16px; position:relative; z-index:1;">
        <div style="
            width:52px; height:52px; border-radius:14px;
            background:linear-gradient(135deg,#00D4AA,#00A884);
            display:flex; align-items:center; justify-content:center;
            font-size:24px;
        ">📈</div>
        <div>
            <div style="color:#00D4AA; font-size:18px; font-weight:700; letter-spacing:2px;">MARKET BRIEF</div>
            <div style="color:rgba(255,255,255,0.45); font-size:13px; letter-spacing:1px;">TODAY'S KEY INSIGHTS</div>
        </div>
    </div>

    <!-- 중앙: 메인 헤드라인 -->
    <div style="position:relative; z-index:1; flex:1; display:flex; flex-direction:column; justify-content:center; padding:60px 0;">
        <div style="
            display:inline-block; width:fit-content;
            background:rgba(0,212,170,0.15); border:1px solid rgba(0,212,170,0.3);
            border-radius:100px; padding:10px 24px; margin-bottom:40px;
            color:#00D4AA; font-size:16px; font-weight:500; letter-spacing:1px;
        ">🔥 오늘의 핵심</div>

        <div style="
            font-size:68px; font-weight:900; line-height:1.15;
            color:#FFFFFF; letter-spacing:-1px;
            word-break:keep-all;
        ">{headline}</div>

        <div style="
            margin-top:40px;
            width:80px; height:4px;
            background:linear-gradient(to right, #00D4AA, transparent);
            border-radius:2px;
        "></div>

        <div style="
            margin-top:32px; font-size:26px; font-weight:400;
            color:rgba(255,255,255,0.6); line-height:1.6; word-break:keep-all;
        ">{subtext}</div>
    </div>

    <!-- 하단: 스와이프 안내 -->
    <div style="
        display:flex; align-items:center; justify-content:space-between;
        position:relative; z-index:1;
        border-top:1px solid rgba(255,255,255,0.08); padding-top:36px;
    ">
        <div style="color:rgba(255,255,255,0.35); font-size:15px;">
            {datetime.now().strftime("%Y년 %m월 %d일")}
        </div>
        <div style="
            display:flex; align-items:center; gap:10px;
            color:rgba(255,255,255,0.5); font-size:15px;
        ">
            <span>스와이프해서 확인</span>
            <span style="color:#00D4AA; font-size:20px;">→</span>
        </div>
    </div>
</div>""")


# ── Card 2: Summary ───────────────────────────────────────────────────────────
def build_card2_summary(analysis):
    points = analysis.get("key_points", [])
    count  = len(points)

    # 개수에 따라 폰트/패딩 조절
    if count <= 4:
        font_size, padding_v, num_size = 30, 40, 52
    elif count <= 6:
        font_size, padding_v, num_size = 26, 28, 44
    else:
        font_size, padding_v, num_size = 22, 20, 38

    items_html = ""
    colors = ["#00D4AA", "#4DA6FF", "#FF6B53", "#A78BFA", "#FBBF24", "#34D399", "#F472B6", "#60A5FA"]
    for i, p in enumerate(points):
        c = colors[i % len(colors)]
        items_html += f"""
        <div style="
            display:flex; align-items:flex-start; gap:24px;
            padding:{padding_v}px 0;
            border-bottom:1px solid rgba(255,255,255,0.07);
        ">
            <div style="
                min-width:{num_size}px; height:{num_size}px; border-radius:50%;
                background:rgba(255,255,255,0.05); border:2px solid {c};
                display:flex; align-items:center; justify-content:center;
                font-size:{num_size // 2}px; font-weight:900; color:{c}; margin-top:2px; flex-shrink:0;
            ">{i+1}</div>
            <div style="font-size:{font_size}px; font-weight:500; color:#FFFFFF; line-height:1.6; word-break:keep-all;">{p}</div>
        </div>
        """

    return html_doc(f"""
<div style="
    width:1080px; height:1440px;
    background: linear-gradient(160deg, #060D1F 0%, #0D1F3C 60%, #091428 100%);
    display:flex; flex-direction:column;
    padding:80px 72px;
    position:relative; overflow:hidden;
">
    <div style="position:absolute;top:-100px;right:-100px;width:500px;height:500px;border-radius:50%;background:radial-gradient(circle,rgba(77,166,255,0.1) 0%,transparent 70%);"></div>

    <!-- 상단 헤더 -->
    <div style="margin-bottom:48px;">
        <div style="color:#4DA6FF; font-size:16px; font-weight:700; letter-spacing:2px; margin-bottom:20px;">📋 오늘의 요약</div>
        <div style="font-size:52px; font-weight:900; color:#FFFFFF; line-height:1.2;">핵심 포인트<br><span style="color:#4DA6FF;">{count}가지</span></div>
        <div style="width:60px;height:4px;background:#4DA6FF;border-radius:2px;margin-top:24px;"></div>
    </div>

    <!-- 포인트 리스트 -->
    <div style="flex:1; overflow:hidden;">
        {items_html}
    </div>

    <!-- 하단 -->
    <div style="
        margin-top:32px; padding-top:28px;
        border-top:1px solid rgba(255,255,255,0.08);
        display:flex; justify-content:space-between; align-items:center;
    ">
        <div style="color:rgba(255,255,255,0.3); font-size:14px; letter-spacing:1px;">MARKET BRIEF</div>
        <div style="color:rgba(255,255,255,0.3); font-size:14px;">2 / 6</div>
    </div>
</div>""")


# ── Card 3-5: Detail ──────────────────────────────────────────────────────────
def build_detail_card(detail, card_num=3):
    title   = detail.get("title", "")
    summary = detail.get("summary", "")
    bullets = detail.get("bullets", [])

    bullets_html = ""
    for b in bullets:
        bullets_html += f"""
        <div style="
            display:flex; align-items:flex-start; gap:18px;
            margin-bottom:28px;
        ">
            <div style="
                min-width:8px; height:8px; border-radius:50%;
                background:#FF6B53; margin-top:14px;
            "></div>
            <div style="font-size:27px; color:rgba(255,255,255,0.8); line-height:1.65; word-break:keep-all; font-weight:400;">{b}</div>
        </div>
        """

    accent_colors = {3: "#FF6B53", 4: "#A78BFA", 5: "#FBBF24"}
    accent = accent_colors.get(card_num, "#00D4AA")

    return html_doc(f"""
<div style="
    width:1080px; height:1440px;
    background: linear-gradient(160deg, #060D1F 0%, #0D1F3C 60%, #091428 100%);
    display:flex; flex-direction:column;
    padding:80px 72px;
    position:relative; overflow:hidden;
">
    <div style="position:absolute;bottom:-100px;right:-100px;width:450px;height:450px;border-radius:50%;background:radial-gradient(circle,{accent}22 0%,transparent 70%);"></div>

    <!-- 카드 번호 뱃지 -->
    <div style="
        display:flex; align-items:center; gap:16px; margin-bottom:56px;
    ">
        <div style="
            padding:8px 20px; border-radius:100px;
            background:{accent}22; border:1px solid {accent}55;
            color:{accent}; font-size:15px; font-weight:700; letter-spacing:1px;
        ">DETAIL {card_num - 1}</div>
        <div style="flex:1;height:1px;background:rgba(255,255,255,0.08);"></div>
        <div style="color:rgba(255,255,255,0.3);font-size:14px;">{card_num} / 6</div>
    </div>

    <!-- 타이틀 -->
    <div style="
        font-size:54px; font-weight:900; color:#FFFFFF;
        line-height:1.2; word-break:keep-all; margin-bottom:12px;
    ">{title}</div>
    <div style="width:60px;height:4px;background:{accent};border-radius:2px;margin-bottom:48px;"></div>

    <!-- 요약 -->
    <div style="
        background:rgba(255,255,255,0.04); border-left:4px solid {accent};
        border-radius:0 16px 16px 0; padding:32px 36px; margin-bottom:52px;
        font-size:28px; color:rgba(255,255,255,0.75); line-height:1.65;
        font-weight:400; word-break:keep-all;
    ">{summary}</div>

    <!-- 불릿 -->
    <div style="flex:1;">
        {bullets_html}
    </div>

    <!-- 하단 -->
    <div style="
        padding-top:32px; border-top:1px solid rgba(255,255,255,0.08);
        display:flex; justify-content:space-between; align-items:center;
    ">
        <div style="color:rgba(255,255,255,0.3);font-size:14px;letter-spacing:1px;">MARKET BRIEF</div>
        <div style="color:{accent};font-size:14px;">→ 다음 카드</div>
    </div>
</div>""")


# ── Card 6: CTA ───────────────────────────────────────────────────────────────
def build_card6_cta(cta):
    summary = cta.get("summary", "")
    action  = cta.get("action", "")

    return html_doc(f"""
<div style="
    width:1080px; height:1440px;
    background: linear-gradient(160deg, #060D1F 0%, #0D1F3C 60%, #091428 100%);
    display:flex; flex-direction:column;
    justify-content:space-between;
    padding:80px 72px;
    position:relative; overflow:hidden;
">
    <div style="position:absolute;top:-80px;left:-80px;width:480px;height:480px;border-radius:50%;background:radial-gradient(circle,rgba(0,212,170,0.12) 0%,transparent 70%);"></div>
    <div style="position:absolute;bottom:-60px;right:-60px;width:380px;height:380px;border-radius:50%;background:radial-gradient(circle,rgba(255,107,53,0.1) 0%,transparent 70%);"></div>

    <!-- 상단 -->
    <div style="
        display:flex; align-items:center; gap:16px;
    ">
        <div style="
            width:52px; height:52px; border-radius:14px;
            background:linear-gradient(135deg,#00D4AA,#00A884);
            display:flex; align-items:center; justify-content:center;
            font-size:24px;
        ">📈</div>
        <div style="color:#00D4AA; font-size:18px; font-weight:700; letter-spacing:2px;">MARKET BRIEF</div>
    </div>

    <!-- 중앙 -->
    <div style="flex:1; display:flex; flex-direction:column; justify-content:center; padding:40px 0;">
        <div style="
            font-size:20px; font-weight:700; color:#00D4AA;
            letter-spacing:2px; margin-bottom:32px;
        ">💡 오늘의 투자 인사이트</div>

        <div style="
            font-size:52px; font-weight:900; color:#FFFFFF;
            line-height:1.3; word-break:keep-all; margin-bottom:48px;
        ">{summary}</div>

        <div style="
            width:80px; height:4px;
            background:linear-gradient(to right, #00D4AA, #4DA6FF);
            border-radius:2px; margin-bottom:48px;
        "></div>

        <!-- 액션 박스 -->
        <div style="
            background:linear-gradient(135deg, rgba(0,212,170,0.15), rgba(77,166,255,0.1));
            border:1px solid rgba(0,212,170,0.3);
            border-radius:24px; padding:48px;
        ">
            <div style="font-size:18px; color:rgba(255,255,255,0.5); margin-bottom:16px; letter-spacing:1px;">ACTION POINT</div>
            <div style="font-size:34px; font-weight:700; color:#FFFFFF; line-height:1.5; word-break:keep-all;">{action}</div>
        </div>
    </div>

    <!-- 하단 팔로우 유도 -->
    <div style="
        border-top:1px solid rgba(255,255,255,0.08); padding-top:40px;
        display:flex; flex-direction:column; gap:24px;
    ">
        <div style="
            display:flex; align-items:center; justify-content:center;
            gap:16px;
        ">
            <div style="flex:1;height:1px;background:rgba(255,255,255,0.08);"></div>
            <div style="
                padding:14px 32px; border-radius:100px;
                background:linear-gradient(135deg,#00D4AA,#4DA6FF);
                font-size:20px; font-weight:700; color:#060D1F;
            ">팔로우하고 매일 받아보기 →</div>
            <div style="flex:1;height:1px;background:rgba(255,255,255,0.08);"></div>
        </div>
        <div style="text-align:center; color:rgba(255,255,255,0.3); font-size:14px;">
            6 / 6 · MARKET BRIEF
        </div>
    </div>
</div>""")


# ── Main ──────────────────────────────────────────────────────────────────────
def generate_all_cards(result, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M")
    base = Path(output_dir)

    analysis = result.get("analysis", {})
    details  = result.get("details", [])
    cta      = result.get("cta", {})

    cards = [
        build_card1_hook(analysis),
        build_card2_summary(analysis),
        build_detail_card(details[0], card_num=3),
        build_detail_card(details[1], card_num=4),
        build_detail_card(details[2], card_num=5),
        build_card6_cta(cta),
    ]

    from playwright.sync_api import sync_playwright

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for i, html in enumerate(cards, 1):
            file = base / f"card{i}_{ts}.png"

            page = browser.new_page(viewport={"width": 1080, "height": 1440})
            page.set_content(html)
            page.wait_for_timeout(2000)
            page.screenshot(path=str(file), full_page=False)

            results.append(str(file))

        browser.close()

    return results
