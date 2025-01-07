from crawl4ai import AsyncWebCrawler, CacheMode
from datetime import datetime
from src.models.data_models import FinancialData
from src.utils.database import insert_scraped_data
from src.utils.config import SCRAPER_SETTINGS, REDIS, LLM_SETTINGS
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM 

# Initialize the web crawler
# crawler = AsyncWebCrawler(cache_mode=CacheMode.MEMORY, redis_host=REDIS["host"], redis_port=REDIS["port"])
crawler = AsyncWebCrawler()

pipe = pipeline("text-generation", model="meta-llama/Llama-3.2-1B")     
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.2-1B")
model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-3.2-1B")

# Initialize sentiment analysis pipeline
sentiment_analyzer = pipeline("sentiment-analysis", model=LLM_SETTINGS["model"], device=0)

async def scrape_sources():
    """
    Scrapes financial data from configured sources and saves them in the database.
    """
    batch_records = []
    for source in SCRAPER_SETTINGS["sources"]:
        print(f"Scraping: {source['name']}")
        response = await crawler.fetch(source["url"])
        if not response or response.status != 200:
            print(f"Failed to fetch {source['url']}")
            continue

        # Extract headlines or relevant data (this parser depends on the source structure)
        articles = parse_html(response.text)
        for article in articles:
            # Perform sentiment analysis and summarization
            sentiment = sentiment_analyzer(article["headline"])[0]["label"]
            summary = summarize_text(article["content"])

            # Create a unified data record
            record = FinancialData(
                source=source["name"],
                symbol=article.get("symbol"),
                headline=article["headline"],
                summary=summary,
                sentiment=sentiment,
                publish_date=datetime.strptime(article["publish_date"], "%Y-%m-%d")
            ).dict()

            batch_records.append(record)

            # Batch insert data into database
            if len(batch_records) >= SCRAPER_SETTINGS["batch_size"]:
                insert_scraped_data(batch_records)
                batch_records.clear()

    # Insert any remaining records
    if batch_records:
        insert_scraped_data(batch_records)

def parse_html(html):
    """
    Parses HTML content to extract articles.
    Replace this with your own parsing logic for each source.
    """
    # Example data structure
    return [
        {"headline": "Tesla beats Q4 expectations", "content": "Tesla's revenue grew 30%...", "publish_date": "2025-01-01", "symbol": "TSLA"},
        {"headline": "Apple unveils new iPhone", "content": "The latest iPhone features...", "publish_date": "2025-01-02", "symbol": "AAPL"},
    ]

def summarize_text(text):
    """
    Summarize the given text using an LLM.
    Replace this with API calls to Ollama or another LLM service if necessary.
    """
    return f"Summary of: {text[:100]}..."  # Placeholder logic
