

## 📌 README.md

```md
# 📊 Instagram Market Briefing Bot

주식 시장 데이터를 수집하고 AI를 활용하여  
인스타그램용 카드뉴스를 자동 생성하는 프로젝트입니다.

---

## 🚀 기능

- 📈 실시간 시장 데이터 수집 (S&P500, NASDAQ, KOSPI, 환율)
- 🤖 AI 기반 시장 분석 (Claude)
- 🧠 뉴스 기반 투자 인사이트 생성
- 🖼️ 카드뉴스 이미지 자동 생성 (1080x1080)
- 💾 결과 JSON 저장 (재사용 및 디버깅)

---

## ⚙️ 전체 동작 흐름

```

1. 시장 데이터 수집
2. Claude AI 분석 요청
3. JSON 결과 생성
4. 카드 이미지 생성

```

---

## 📂 프로젝트 구조

```

.
├── main.py
├── services/
│   ├── market_data.py   # 시장 데이터 수집
│   └── claude.py       # AI 분석
├── generator/
│   └── card_generator.py  # 카드 이미지 생성
├── utils/
│   └── json_parser.py
├── data/               # 분석 결과 JSON 저장
├── output/             # 생성된 이미지

```

---

## 🔑 환경 설정

### 1. Python 가상환경

```

python3 -m venv venv
source venv/bin/activate

```

---

### 2. 패키지 설치

```

pip install -r requirements.txt
playwright install

```

---

### 3. Claude API Key 설정

```

export ANTHROPIC_API_KEY=your_api_key

```

---

## ▶️ 실행 방법

```

python main.py

```

---

## 🧠 핵심 기술

- yfinance → 시장 데이터 수집
- Claude API → 콘텐츠 생성
- Playwright → 이미지 렌더링

---

## ⚠️ 주의사항

- Claude 모델명이 정확해야 정상 동작
- AI 응답이 JSON 형식을 깨뜨릴 수 있음
- data/ 디렉토리의 JSON을 활용하면 재호출 없이 테스트 가능

---

## 🔥 향후 개선

- 뉴스 자동 수집 (RSS)
- 업로드 자동화 (Instagram API)
- A/B 테스트 시스템
- 조회수 기반 콘텐츠 최적화

---

## 💡 핵심 아이디어

```

AI를 활용해 “정보”를 “콘텐츠”로 바꾼다

```
```