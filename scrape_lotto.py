import asyncio
import json
import re
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from database import SessionLocal, LotteryResult, init_db
from sqlalchemy import func

class LottoScraper:
    def __init__(self):
        self.thai_months = {
            "มกราคม": 1, "กุมภาพันธ์": 2, "มีนาคม": 3, "เมษายน": 4,
            "พฤษภาคม": 5, "มิถุนายน": 6, "กรกฎาคม": 7, "สิงหาคม": 8,
            "กันยายน": 9, "ตุลาคม": 10, "พฤศจิกายน": 11, "ธันวาคม": 12
        }
        init_db()

    def _parse_thai_date(self, text):
        # looks for format like: "1 มีนาคม 2569"
        pattern = r'(\d{1,2})\s+([ก-๛]+)\s+(\d{4})'
        match = re.search(pattern, text)
        if match:
            day = int(match.group(1))
            month_str = match.group(2)
            year_be = int(match.group(3))
            
            month = self.thai_months.get(month_str)
            if month:
                year_ce = year_be - 543
                try:
                    dt = datetime(year_ce, month, day)
                    return dt
                except ValueError:
                    return None
        return None

    def _determine_lottery_type(self, title, body_text):
        title_norm = title.lower()
        
        if 'ฮานอยพิเศษ' in title_norm:
            return 'ฮานอยพิเศษ'
        if 'ฮานอย vip' in title_norm:
            return 'ฮานอย VIP'
        if 'ฮานอย' in title_norm:
            return 'ฮานอย'
        if 'ลาวสตาร์ vip' in title_norm:
            return 'ลาวสตาร์ VIP'
        if 'ลาวสตาร์' in title_norm:
            return 'ลาวสตาร์'
        if 'ลาว vip' in title_norm:
            return 'ลาว VIP'
        if 'ลาว' in title_norm:
            return 'ลาวพัฒนา'
        if 'สลากกินแบ่งรัฐบาล' in title_norm or 'หวยรัฐบาล' in title_norm:
            return 'ไทย'
            
        full_text = f"{title} {body_text}"
        if 'ฮานอยพิเศษ' in full_text:
            return 'ฮานอยพิเศษ'
        if 'ฮานอย vip' in full_text:
            return 'ฮานอย VIP'
        if 'ฮานอย' in full_text:
            return 'ฮานอย'
        if 'ลาวสตาร์ vip' in full_text:
            return 'ลาวสตาร์ VIP'
        if 'ลาวสตาร์' in full_text:
            return 'ลาวสตาร์'
        if 'ลาว vip' in full_text:
            return 'ลาว VIP'
        if 'ลาวพัฒนา' in full_text or 'หวยลาว' in full_text:
            return 'ลาวพัฒนา'
        
        return 'ไทย'

    def _get_sanook_id(self, url):
        match = re.search(r'/news/(\d+)/', url)
        return match.group(1) if match else None

    async def scrape_article(self, page, url):
        sanook_id = self._get_sanook_id(url)
        if not sanook_id:
            return None

        # Check if already in DB
        db = SessionLocal()
        existing = db.query(LotteryResult).filter(LotteryResult.sanook_id == sanook_id).first()
        db.close()
        if existing:
            print(f"  ⏭️ Already exists (ID: {sanook_id}), skipping.")
            return "EXISTS"

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            await page.wait_for_timeout(3000) 
            content = await page.content()
        except Exception as e:
            print(f"Error loading {url}: {e}")
            return None

        soup = BeautifulSoup(content, 'html.parser')
        
        title_tag = soup.find('h1')
        title = title_tag.text.strip() if title_tag else "Unknown Title"
        
        body_text = soup.get_text()
        lottery_type = self._determine_lottery_type(title, body_text)
        draw_dt = self._parse_thai_date(title) or self._parse_thai_date(body_text)
        
        # 3. Extract Lottery Numbers
        data = {}
        lotto_container = soup.find('div', class_='sn-lt-lotto')
        if lotto_container:
            prize_items = lotto_container.find_all('div', class_=re.compile(r'sn-lt-lotto__top'))
            for item in prize_items:
                strong_label = item.find('strong')
                if not strong_label:
                    continue
                
                label_text = strong_label.get_text(strip=True)
                prize_divs = item.find_all('div')
                numbers = [d.get_text(strip=True) for d in prize_divs if d.get_text(strip=True).isdigit()]
                
                if not numbers:
                    continue

                if label_text.startswith("รางวัลที่ 1") and "ข้างเคียง" not in label_text:
                    data["รางวัลที่หนึ่ง"] = " ".join(numbers)
                elif "เลขหน้า 3 ตัว" in label_text:
                    data["เลขหน้า_3_ตัว"] = " ".join(numbers)
                elif "เลขท้าย 3 ตัว" in label_text:
                    data["เลขท้าย_3_ตัว"] = " ".join(numbers)
                elif "เลขท้าย 2 ตัว" in label_text:
                    data["เลขท้าย_2_ตัว"] = " ".join(numbers)
                elif "รางวัลข้างเคียง" in label_text:
                    data["รางวัลข้างเคียง"] = " ".join(numbers)

        if not data:
            # Fallback: Extract all 2-6 digit numbers from strong, b, span, and p tags
            potential_tags = soup.find_all(['strong', 'b', 'span', 'p'])
            all_text = " ".join([t.get_text(strip=True) for t in potential_tags])
            
            # Find common lottery number patterns (2, 3, 4, 5, 6 digits)
            found_numbers = re.findall(r'\b\d{2,6}\b', all_text)
            unique_numbers = []
            for n in found_numbers:
                if n not in unique_numbers:
                    unique_numbers.append(n)
            
            if unique_numbers:
                # Prioritize longer numbers as first prize
                sorted_nums = sorted(unique_numbers, key=len, reverse=True)
                data["รางวัลที่หนึ่ง"] = sorted_nums[0]
                for idx, num in enumerate(sorted_nums[:10]):
                    data[f"number_{idx}"] = num

        # --- VALIDATION LAYER ---
        is_valid = False
        if lottery_type == "ไทย":
            required = ["รางวัลที่หนึ่ง", "เลขหน้า_3_ตัว", "เลขท้าย_3_ตัว", "เลขท้าย_2_ตัว"]
            is_valid = all(k in data for k in required)
            if not is_valid:
                # Secondary check for Thai: if we have 1st, 2-digit, and 3-digit somewhere
                is_valid = "รางวัลที่หนึ่ง" in data and any("3_ตัว" in k for k in data) and "เลขท้าย_2_ตัว" in data
                if not is_valid:
                    print(f"  ❌ Invalid Thai Lottery: Missing essential prizes. {list(data.keys())}")
        else:
            # Lao/Hanoi must have at least one significant number found
            is_valid = len(data) > 0 and ("รางวัลที่หนึ่ง" in data or "number_0" in data)
            if not is_valid:
                # Debug print to see what it sees
                sample_txt = soup.get_text()[:200].replace("\n", " ")
                print(f"  ❌ Invalid {lottery_type}: No numbers found. Sample: {sample_txt}")

        if not is_valid:
            return None # Don't save if invalid

        return {
            "sanook_id": sanook_id,
            "url": url,
            "title": title,
            "type": lottery_type,
            "date": draw_dt.date() if draw_dt else None,
            "data": data,
            "scraped_at": datetime.now()
        }

    async def get_articles_from_api(self, max_articles=20):
        print("Fetching articles from Sanook GraphQL API...")
        api_url = "https://graph.sanook.com/"
        
        keywords = ["ตรวจหวย", "หวยลาว", "หวยฮานอย", "ฮานอยพิเศษ", "ฮานอย vip", "ลาวสตาร์", "ลาว vip"]
        lottery_urls = []
        seen_urls = set()
        
        async with async_playwright() as p:
            request_context = await p.request.new_context()
            
            for keyword in keywords:
                has_next = True
                after_cursor = None
                keyword_article_count = 0
                
                while has_next and keyword_article_count < (max_articles // len(keywords)):
                    variables = {
                        "oppaChannel": "news",
                        "channels": ["news"],
                        "orderBy": {"field": "CREATED_AT", "direction": "DESC"},
                        "first": 15,
                        "keyword": keyword,
                        "after": after_cursor
                    }
                    extensions = {
                        "persistedQuery": {
                            "version": 1,
                            "sha256Hash": "98d212b4c53a3670ec293293f18296dc5472b97ab7cbbd7b429b9aa225b284d8"
                        }
                    }
                    
                    params = {
                        "operationName": "getArchiveEntries",
                        "variables": json.dumps(variables),
                        "extensions": json.dumps(extensions)
                    }
                    
                    response = await request_context.get(api_url, params=params)
                    if response.ok:
                        res_data = await response.json()
                        entries = res_data.get("data", {}).get("entries", {})
                        edges = entries.get("edges", [])
                        
                        if not edges:
                            break
                            
                        for edge in edges:
                            node = edge.get("node", {})
                            title = node.get("title", "")
                            is_result = any(k in title for k in ["ตรวจหวย", "ผลหวย", "ตรวจผลหวย"])
                            if is_result:
                                url = f"https://www.sanook.com/news/{node.get('id')}/"
                                if url not in seen_urls:
                                    lottery_urls.append(url)
                                    seen_urls.add(url)
                                    keyword_article_count += 1
                        
                        page_info = entries.get("pageInfo", {})
                        has_next = page_info.get("hasNextPage", False)
                        after_cursor = page_info.get("endCursor")
                    else:
                        break
            
            await request_context.dispose()
            
        print(f"Found {len(lottery_urls)} unique articles.")
        return lottery_urls[:max_articles]

    async def run(self, max_articles=50):
        print(f"Starting LottoScraper for max {max_articles} articles...")
        lottery_urls = await self.get_articles_from_api(max_articles)
        
        def get_id(url):
            return int(self._get_sanook_id(url) or 0)
            
        lottery_urls.sort(key=get_id, reverse=True)
        # Use the limit provided by the user
        lottery_urls = lottery_urls[:max_articles] 

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context()
            page = await context.new_page()

            db_results = []
            for i, url in enumerate(lottery_urls):
                print(f"[{i+1}/{len(lottery_urls)}] Processing: {url}")
                article_data = await self.scrape_article(page, url)
                
                if article_data == "EXISTS":
                    continue

                if article_data:
                    db_results.append(article_data)
                    print(f"  📌 [{article_data['type']}] Scraped successfully.")
                
                await asyncio.sleep(1)

            await browser.close()

            if db_results:
                self._save_to_db(db_results)
            else:
                print("No new data to save.")

    def _save_to_db(self, results):
        db = SessionLocal()
        new_count = 0
        for res in results:
            lotto = LotteryResult(
                sanook_id=res["sanook_id"],
                type=res["type"],
                draw_date=res["date"],
                draw_title=res["title"],
                prizes=res["data"],
                url=res["url"],
                scraped_at=res["scraped_at"]
            )
            db.add(lotto)
            new_count += 1
        
        try:
            db.commit()
            print(f"✅ Successfully saved {new_count} new records to the database.")
        except Exception as e:
            db.rollback()
            print(f"❌ Error saving to DB: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Sanook Lottery Scraper")
    parser.add_argument("--limit", type=int, default=20, help="Maximum number of articles to scrape (default: 20)")
    parser.add_argument("--clear", action="store_true", help="Clear all data from database before scraping")
    args = parser.parse_args()

    # Clear Logic
    if args.clear:
        print("⚠️  Clearing all data from database...")
        db = SessionLocal()
        try:
            db.query(LotteryResult).delete()
            db.commit()
            print("✅ Database cleared successfully.")
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
            db.rollback()
        finally:
            db.close()

    async def main():
        scraper = LottoScraper()
        await scraper.run(max_articles=args.limit)
    
    asyncio.run(main())
