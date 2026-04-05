import yfinance as yf
import feedparser


def get_indices():
    tickers = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "KOSPI": "^KS11",
        "USD/KRW": "KRW=X"
    }

    result = {}

    for name, ticker in tickers.items():
        data = yf.Ticker(ticker).history(period="2d")

        if len(data) < 2:
            continue

        prev = data["Close"].iloc[-2]
        curr = data["Close"].iloc[-1]

        change = curr - prev
        change_pct = (change / prev) * 100

        result[name] = {
            "price": float(curr),
            "change": float(change),
            "change_pct": float(change_pct),
            "direction": "up" if change > 0 else "down"
        }

    return result


def get_market_news():
    feeds = [
        "https://feeds.reuters.com/reuters/businessNews",
        "https://www.cnbc.com/id/100003114/device/rss/rss.html"
        "https://news.google.com/rss/search?q=주식"
    ]

    news = []

    for url in feeds:
        feed = feedparser.parse(url)
        for entry in feed.entries[:3]:
            news.append(entry.title)

    return news[:5]


def get_market_data():
    return {
        "indices": get_indices(),
        "news": get_market_news()
    }
