# Sanook Lottery Scraper 🎰

A Python web scraper using Playwright that extracts lottery data from Sanook News articles containing "ตรวจหวย" (lottery check) information.

## Features

- ✅ Scrapes lottery news articles from Sanook (https://www.sanook.com/news/)
- ✅ Filters articles containing "ตรวจหวย" (lottery check keywords)
- ✅ Extracts lottery type (สลากกินแบ่งรัฐบาล, etc.)
- ✅ Parses Thai date format and converts to ISO format (YYYY-MM-DD)
- ✅ Extracts lottery numbers and prize information
- ✅ Exports data to JSON format
- ✅ Async/await for efficient scraping
- ✅ Error handling and retry logic

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browsers

```bash
playwright install chromium
```

## Usage

### Basic Usage

```bash
python scrape_lotto.py
```

This will:
1. Fetch news articles from Sanook
2. Check each article for lottery-related content
3. Scrape articles containing "ตรวจหวย"
4. Save results to `lotto_data.json`

### Advanced Usage (Custom Script)

```python
import asyncio
from scrape_lotto import LottoScraper

async def main():
    scraper = LottoScraper(output_file="my_lotto_data.json")
    await scraper.run(
        start_url="https://www.sanook.com/news/",
        max_articles=20  # Increase to scrape more articles
    )

asyncio.run(main())
```

## Output Format

The script generates `lotto_data.json` with the following structure:

```json
[
  {
    "url": "https://www.sanook.com/news/9875970/",
    "title": "ตรวจหวย สลากกินแบ่งรัฐบาล งวดที่ 1 มีนาคม 2569",
    "type": "สลากกินแบ่งรัฐบาล",
    "draw": "งวดประจำวันที่ 1 มีนาคม 2569",
    "date": "2026-03-01",
    "data": {
      "number_0": "123456",
      "number_1": "654321",
      "รางวัลที่หนึ่ง": "123456 654321"
    },
    "scraped_at": "2026-03-02T12:34:56.789123"
  }
]
```

### Data Fields

| Field | Description |
|-------|-------------|
| `url` | Source article URL |
| `title` | Article title |
| `type` | Lottery type (สลากกินแบ่งรัฐบาล, หวยออนไลน์, etc.) |
| `draw` | Draw period info (e.g., "งวดประจำวันที่ 1 มีนาคม 2569") |
| `date` | Draw date in ISO format (YYYY-MM-DD) |
| `data` | Extracted lottery numbers and prizes |
| `scraped_at` | Timestamp when data was scraped |

## Configuration

You can customize the scraper behavior:

```python
scraper = LottoScraper(output_file="custom_output.json")

await scraper.run(
    start_url="https://www.sanook.com/news/",
    max_articles=15  # Number of lottery articles to collect
)
```

## Supported Lottery Types

The scraper recognizes and categorizes:
- **สลากกินแบ่งรัฐบาล** - Thai Government Lottery
- **หวยออนไลน์** - Online Lottery
- **หวยยี่กี** - Huay Yee Kee
- **หวยทั่วไป** - General Lottery

## Date Parsing

The script automatically:
- Extracts Thai date format (e.g., "1 มีนาคม 2569")
- Converts Thai Buddhist Era (BE) to Common Era (CE)
- Outputs ISO format dates (YYYY-MM-DD)

### Thai Month Reference

| Thai | CE | Thai | CE |
|------|-----|------|-----|
| มกราคม | 1 | กรกฎาคม | 7 |
| กุมภาพันธ์ | 2 | สิงหาคม | 8 |
| มีนาคม | 3 | กันยายน | 9 |
| เมษายน | 4 | ตุลาคม | 10 |
| พฤษภาคม | 5 | พฤศจิกายน | 11 |
| มิถุนายน | 6 | ธันวาคม | 12 |

## Error Handling

The scraper includes:
- Timeout handling (10 seconds per page)
- Network error recovery
- Invalid date handling
- Missing content fallbacks

## Performance Tips

1. **Headless Mode**: Uses headless browser (faster, lower resources)
2. **Async Processing**: Concurrent page loading
3. **Network Waits**: Waits for network idle before scraping
4. **Selective Scraping**: Only fully processes lottery articles

## Troubleshooting

### "No module named 'playwright'"
```bash
pip install -r requirements.txt
playwright install chromium
```

### "Connection refused" or timeout errors
- Check internet connection
- Sanook website may be rate-limiting; add delays:
  ```python
  await page.wait_for_timeout(3000)  # 3 seconds
  ```

### Missing lottery numbers in output
- The HTML structure may have changed on Sanook's website
- Update the `extract_lottery_numbers()` method to match new selectors
- Check the raw HTML structure with browser developer tools

### Thai date parsing not working
- Verify the Thai date format matches expected patterns
- Check for special characters or formatting

## Extending the Scraper

### Add Custom Filters

```python
async def scrape_article(self, page, url):
    # ... existing code ...
    
    # Add custom filtering
    if "2569" not in body_text:  # Only 2026 (BE 2569)
        return None
    
    # ... rest of code ...
```

### Change Output Format

```python
async def save_to_csv(self):
    import csv
    with open("lotto_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["url", "type", "date", "data"])
        writer.writeheader()
        writer.writerows(self.lotto_data)
```

### Add Database Storage

```python
async def save_to_database(self, db_connection):
    for article in self.lotto_data:
        db_connection.insert("lottery_articles", article)
```

## Legal Notice

This scraper is for educational purposes. Always:
- Check the website's `robots.txt` and terms of service
- Don't overload the server with requests
- Respect copyright and data usage rights
- Use appropriate delays between requests

## License

MIT License - Feel free to use and modify for your needs.

## Support

For issues or improvements, check:
- Playwright documentation: https://playwright.dev/python/
- BeautifulSoup documentation: https://www.crummy.com/software/BeautifulSoup/
- Sanook News: https://www.sanook.com/news/

---

Happy scraping! 🎰🎉
# lotto-db
