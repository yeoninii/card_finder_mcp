import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

async def get_card_benefit_info(url: str) -> dict:

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            #await page.goto(url, wait_until="networkidle")
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

# --- 코드 실행 예시 ---
async def main():
    url_to_scrape = "https://www.card-gorilla.com/card/detail/466"
    card_info = await get_card_benefit_info(url_to_scrape)
    import json
    print(json.dumps(card_info, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    asyncio.run(main())