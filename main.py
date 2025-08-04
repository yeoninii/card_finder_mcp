import json
import os
from pathlib import Path
from fastmcp.server import FastMCP, Context
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# 전역 변수로 카드 데이터 저장
CARD_DATA = None
# 모듈 로드 시 카드 데이터를 미리 로드
def load_card_data():
    global CARD_DATA
    json_file_path = Path(__file__).parent / "resources" / "card_with_benefit.json"
    
    try:
        with open(json_file_path, "r", encoding="utf-8") as f:
            CARD_DATA = json.load(f)
        print(f"카드 데이터 로드 완료: {len(CARD_DATA)}개 카드")
    except Exception as e:
        print(f"카드 데이터 로드 실패: {e}")
        CARD_DATA = {"error": f"카드 데이터 로드 실패: {e}"}

# 모듈 로드 시 즉시 실행
load_card_data()

card_mcp = FastMCP("CardSearchServer", instructions='')

@card_mcp.resource(
    uri="resource://card_list",
    name="CardList",
    #description="가지고 있는 모든 카드의 이름과 세부 url이 담긴 json을 반환합니다.",
    description='사용자가 원하는 카드가 해당 목록에 있는지 확인합니다. 목록에 있다면 카드 정보와 상세 url을 같이 반환합니다.',
    #description="전체 카드 목록과 각 카드의 URL을 반환합니다. 특정 카드의 상세 정보 URL을 찾아야 할 때, 이 리스트에서 카드 이름을 검색하여 URL을 확인해야 합니다.",
    mime_type="application/json",
    tags=["search", "card"],
)
def set_all_card_list_info() -> dict:
    '''
    카드 리스트와 카드 상세 정보를 조회할 수 있는 url 정보를 받을 수 있다.

    return: json list
    [
        {
            "card_name": 카드 이름,
            "url": 카드 상세 정보 url
        },
    ]
    '''
    return CARD_DATA


@card_mcp.tool(
        name='GetAllCardListInfo',
        description='사용자의 질문에 나온 카드를 찾기위해 전체 카드리스트를 불러옵니다. 반환되는 결과 값 중에 사용자가 원하는 카드를 선택하면됩니다.',
        tags=['list', 'all']
)
async def get_all_card_list_info(ctx: Context) -> dict:
    '''
    모든 카드리스트 정보를 가져오는 도구입니다.
    해당 도구를 사용해서 사용자가 원하는 카드의 URL을 찾아내세요.
    '''
    # CARD_DATA를 직접 반환
    if CARD_DATA is None:
        return {"error": "카드 데이터가 로드되지 않았습니다."}
    
    return {"cards": CARD_DATA}

@card_mcp.tool(
    name="CardBenefitInfo",
    description="특정 카드의 상세 혜택 정보를 URL을 통해 가져옵니다. **중요: URL은 반드시 'CardList' 리소스(`data://card_list`)를 통해 얻은 값만 사용해야 합니다.** 임의의 웹사이트 URL은 사용할 수 없습니다.",
    tags=["search"],
)
async def get_card_benefit_info(url: str, ctx: Context) -> dict:
    '''
    카드 상세 정보를 가져오는 도구입니다.
    'CardList' 리소스에서 가져온 URL을 사용하여 카드 상세 정보를 조회할 수 있습니다.
    

    parameters:
    - url: 카드 상세 정보 url

    return: json
    {
        "card_name": 카드 이름,
        "url": 카드 상세 정보 url,
        "benefits": 카드 혜택 정보
    }
    '''
    # URL 유효성 검사: CARD_DATA에 해당 URL이 있는지 확인
    if CARD_DATA is None:
        return {"error": "카드 데이터가 로드되지 않았습니다."}
    
    # CARD_DATA가 리스트인지 확인
    if not isinstance(CARD_DATA, list):
        return {"error": "카드 데이터 형식이 올바르지 않습니다."}
    
    # 입력된 URL이 CARD_DATA에 있는지 확인
    url_exists = False
    card_name = ""
    for card in CARD_DATA:
        if isinstance(card, dict) and card.get("url") == url:
            url_exists = True
            card_name = card.get("name", "알 수 없는 카드")
            break
    
    if not url_exists:
        return {"error": f"입력된 URL '{url}'이 카드 데이터에 존재하지 않습니다. 유효한 카드 URL을 입력해주세요."}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_selector("div.bene_area", timeout=30000)
            await page.wait_for_selector("strong.card", timeout=30000)
            
            benefit_buttons_selector = "div.bene_area > dl > dt"
            buttons = await page.query_selector_all(benefit_buttons_selector)
            

            print(f"총 {len(buttons)}개의 혜택을 클릭하여 펼칩니다...")
            for button in buttons:
                await button.click()
                await page.wait_for_timeout(500)

            # 4. 모든 정보가 표시된 최종 HTML 컨텐츠 추출
            html_content = await page.content()

            # 5. BeautifulSoup을 이용해 데이터 정제 및 구조화
            soup = BeautifulSoup(html_content, "html.parser")

            card_name_element = soup.select_one("strong.card")
            card_name = card_name_element.text.strip() if card_name_element else "알 수 없는 카드"

            benefits_data = []
            # # 열려있는 혜택 섹션(li.on)을 순회
            benefit_sections = soup.select("div.bene_area > dl")

            print(f"총 {len(benefit_sections)}개의 리스트를 가져 왔습니다.")
            for dl in benefit_sections:
                category = dl.select_one("p.txt1").text.strip()
                summary = dl.select_one("i").text.strip()
                

                # 상세 정보(<dd>)는 있을 수도, 없을 수도 있습니다.
                details_tag = dl.select_one("dd")
                details = details_tag.get_text(separator="\n", strip=True) if details_tag else "상세 설명 없음"
                
                benefits_data.append({
                    'category': category,
                    'summary': summary,
                    'details': details
                })
            

            # 6. 최종 JSON 결과 생성
            result = {"card_name": card_name, "benefits": benefits_data, "url": url}
            #result = {"card_name": card_name, "url": url, "benefits": benefits_data}
        except Exception as e:
            result = {"error": f"데이터 처리 중 오류 발생: {e}"}

        finally:
            await browser.close()

        return result
    
    
if __name__ == "__main__":
    card_mcp.run(transport="stdio")
