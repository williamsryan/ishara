import praw
import pandas as pd
from textblob import TextBlob
import logging
from src.utils.database import insert_reddit_sentiment_data
from src.utils.config import REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT

# Initialize Reddit API
reddit = praw.Reddit(client_id=REDDIT_CLIENT_ID, client_secret=REDDIT_CLIENT_SECRET, user_agent=REDDIT_USER_AGENT)

def fetch_reddit_posts(subreddit, limit=100):
    """
    Fetch recent posts from a subreddit.

    Args:
        subreddit (str): Name of the subreddit.
        limit (int): Number of posts to fetch.

    Returns:
        list: List of posts with title and content.
    """
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        posts.append({"title": submission.title, "content": submission.selftext})
    return posts

def analyze_sentiment(text):
    """
    Analyze the sentiment of a given text.

    Args:
        text (str): Text to analyze.

    Returns:
        float: Sentiment polarity score (-1 to 1).
    """
    return TextBlob(text).sentiment.polarity

def fetch_reddit_sentiment(subreddits, tickers):
    """
    Fetch sentiment data from Reddit for specified subreddits and tickers.

    Args:
        subreddits (list): List of subreddits.
        tickers (list): List of tickers to filter posts.

    Returns:
        pd.DataFrame: Sentiment data with columns ['ticker', 'subreddit', 'sentiment', 'datetime'].
    """
    sentiment_data = []
    for subreddit in subreddits:
        logging.info(f"Fetching posts from r/{subreddit}...")
        posts = fetch_reddit_posts(subreddit)
        for post in posts:
            for ticker in tickers:
                if ticker in post["title"].upper():
                    sentiment = analyze_sentiment(post["content"])
                    sentiment_data.append({
                        "ticker": ticker,
                        "subreddit": subreddit,
                        "sentiment": sentiment,
                        "datetime": pd.Timestamp.now()
                    })
    return pd.DataFrame(sentiment_data)

def insert_reddit_sentiment(subreddits, tickers):
    """
    Fetch and store Reddit sentiment data.

    Args:
        subreddits (list): List of subreddits.
        tickers (list): List of tickers.
    """
    sentiment_data = fetch_reddit_sentiment(subreddits, tickers)
    if not sentiment_data.empty:
        insert_reddit_sentiment_data(sentiment_data.to_dict("records"))
        logging.info("✅ Reddit sentiment data inserted successfully.")
    else:
        logging.warning("⚠️ No sentiment data fetched.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    subreddits = ["stocks", "wallstreetbets"]
    tickers = ["AAPL", "MSFT", "TSLA"]
    insert_reddit_sentiment(subreddits, tickers)
    