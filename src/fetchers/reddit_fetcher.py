import praw
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from src.utils.database import insert_alternative_data

def fetch_reddit_sentiment(subreddit, keyword):
    """
    Fetch Reddit posts and analyze sentiment using the official Reddit API.
    """
    # Reddit API credentials (add these to config.py)
    CLIENT_ID = "your_client_id"
    CLIENT_SECRET = "your_client_secret"
    USER_AGENT = "your_user_agent"

    reddit = praw.Reddit(client_id=CLIENT_ID, client_secret=CLIENT_SECRET, user_agent=USER_AGENT)
    analyzer = SentimentIntensityAnalyzer()

    data_to_insert = []
    try:
        print(f"🔍 Fetching Reddit posts from subreddit '{subreddit}' for keyword '{keyword}'...")
        for submission in reddit.subreddit(subreddit).search(keyword, limit=10):
            text = (submission.title + " " + submission.selftext).strip()
            if not text:
                continue

            sentiment = analyzer.polarity_scores(text)["compound"]
            timestamp = datetime.utcfromtimestamp(submission.created_utc)

            data_to_insert.append(("reddit", keyword, timestamp, "sentiment_score", sentiment, text[:500]))
        
        if data_to_insert:
            print(f"✅ Inserting {len(data_to_insert)} Reddit records into the database...")
            insert_alternative_data(data_to_insert)
        else:
            print(f"⚠️ No valid Reddit posts found for keyword '{keyword}'.")
    except Exception as e:
        print(f"❌ Error fetching Reddit data: {e}")

if __name__ == "__main__":
    fetch_reddit_sentiment("stocks", "AAPL")
    