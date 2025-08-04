# MCP Card Finder - 카드 정보 검색 및 추천 시스템

이 프로젝트는 Model Context Protocol (MCP)을 사용하여 다양한 신용카드 정보를 검색하고 추천하는 AI 기반 카드 도우미 시스템입니다. Google Gemini API와 웹 크롤링을 통해 실시간 카드 정보를 제공합니다.

## 🚀 주요 기능

- **카드 검색**: 전체 카드 목록에서 원하는 카드 검색
- **상세 정보 조회**: 카드별 상세 혜택 정보 제공
- **AI 추천**: 사용자 요구사항에 맞는 카드 추천
- **실시간 대화**: 자연어로 카드 관련 질문 및 답변
- **대화 히스토리**: 이전 대화 내용 저장 및 조회

## 📁 프로젝트 구조

```
mcp_card/
├── main.py                 # MCP 서버 (카드 정보 제공)
├── mcp_client.py          # MCP 클라이언트 (AI 대화 인터페이스)
├── crawling_test.py       # 웹 크롤링 테스트
├── create_mcp_json.py     # MCP 설정 파일 생성
├── mcp_config.json        # MCP 서버 설정
├── requirements.txt       # Python 의존성 패키지
├── README.md             # 프로젝트 문서
└── resources/
    ├── card_urls.json        # 카드 URL 데이터
    └── card_with_benefit.json # 카드 상세 정보 데이터
```

## 🛠️ 설치 및 설정

### 1. 환경 준비

```bash
# 프로젝트 디렉토리로 이동
cd /path/to/mcp_card

# 가상환경 활성화
source venv/bin/activate

# 의존성 패키지 설치
pip install -r requirements.txt
```

### 2. Google API 키 설정

Google AI Studio에서 API 키를 발급받아야 합니다:

1. [Google AI Studio](https://aistudio.google.com/)에 접속
2. API 키 생성
3. 환경변수로 설정

#### 환경변수 설정 (권장)
```bash
export GOOGLE_API_KEY="your_google_api_key_here"
```

#### 코드에 직접 입력
`mcp_client.py` 파일에서 다음 줄의 주석을 해제하고 API 키를 입력:
```python
google_api_key = "your_google_api_key_here"
```

## 🚀 사용 방법

### 1. MCP 서버 실행

```bash
# MCP 서버 시작 (백그라운드에서 실행)
python main.py
```

### 2. 클라이언트 실행

```bash
# AI 카드 도우미 시작
python mcp_client.py
```

### 3. 사용 예시

```
💬 사용자: 지하철 카드 추천해줘
💬 사용자: 연회비가 낮은 카드 알려줘
💬 사용자: 해외여행 카드 추천해줘
💬 사용자: 현대카드 중에서 추천해줘
💬 사용자: help
💬 사용자: history
💬 사용자: clear
```

## 🔧 주요 명령어

- `help`: 사용 가능한 명령어 및 예시 보기
- `history`: 대화 히스토리 조회
- `clear`: 대화 히스토리 초기화
- `quit` 또는 `exit`: 프로그램 종료

## 🤖 사용 가능한 AI 모델

현재 설정된 모델: `gemini-2.5-flash` (최신 Gemini 2.5 Flash)

다른 모델로 변경하려면 `mcp_client.py`에서 다음 부분을 수정:
```python
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # 다른 모델명으로 변경
    google_api_key=google_api_key,
    temperature=0.1
)
```

### 사용 가능한 Gemini 모델

- `gemini-1.5-flash` (빠르고 효율적)
- `gemini-1.5-pro` (더 정확하고 강력)
- `gemini-2.5-flash` (최신 Gemini 2.5 Flash 모델) ⭐ 현재 사용 중
- `gemini-2.5-pro` (최신 Gemini 2.5 Pro 모델)
- `gemini-2.5-flash-lite` (비용 효율적인 Gemini 2.5 Flash-Lite)

## 🔍 MCP 도구 및 리소스

### 도구 (Tools)

1. **GetAllCardListInfo**: 전체 카드 목록 조회
   - 사용자의 질문에 나온 카드를 찾기 위한 전체 카드리스트 제공
   - 반환되는 결과에서 원하는 카드 선택 가능

2. **CardBenefitInfo**: 카드 상세 혜택 정보 조회
   - 특정 카드의 상세 혜택 정보를 URL을 통해 가져옴
   - **중요**: URL은 반드시 'CardList' 리소스를 통해 얻은 값만 사용

### 리소스 (Resources)

1. **CardList** (`resource://card_list`): 전체 카드 목록
   - 모든 카드의 이름과 상세 정보 URL 포함
   - JSON 형태로 제공

## 📊 데이터 구조

### 카드 정보 형식
```json
{
    "card_name": "카드 이름",
    "url": "카드 상세 정보 URL",
    "benefits": "카드 혜택 정보"
}
```

## ⚠️ 주의사항

- Google API 키는 안전하게 보관하세요
- API 사용량에 따라 요금이 발생할 수 있습니다
- 환경변수 사용을 권장합니다
- 카드 정보는 정기적으로 업데이트가 필요합니다

## 🔄 데이터 업데이트

카드 정보를 업데이트하려면:

1. `crawling_test.py`를 사용하여 새로운 카드 정보 수집
2. `create_mcp_json.py`를 실행하여 MCP 설정 파일 생성
3. `resources/` 폴더의 JSON 파일들 업데이트

## 🛠️ 개발 환경

- **Python**: 3.12+
- **주요 라이브러리**:
  - `fastmcp`: MCP 서버 구현
  - `langchain`: AI 체인 및 도구 관리
  - `google-generativeai`: Google Gemini API
  - `playwright`: 웹 크롤링
  - `beautifulsoup4`: HTML 파싱

## 📝 라이선스

이 프로젝트는 교육 및 연구 목적으로 개발되었습니다.

## 🤝 기여

버그 리포트나 기능 제안은 이슈를 통해 제출해주세요. 