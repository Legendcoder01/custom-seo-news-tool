import feedparser
import newspaper
from newspaper import Article
from datetime import datetime, timedelta
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mocked list of tech news RSS feeds
MOCK_FEEDS = [
    "https://technode.com/feed/",
    "https://www.theverge.com/rss/index.xml",
    "https://hnrss.org/frontpage"
    "https://www.siasat.com/feed/"
    "https://www.abplive.com/trending/feed"
    "https://www.news18.com/commonfeeds/v1/eng/rss/movies.xml"
    "https://hauterrfly.com/entertainment/feed/"
    "https://www.hindustantimes.com/feeds/rss/entertainment/rssfeed.xml"
    "https://www.freepressjournal.in/stories.rss"
    "https://hindi.newsbytesapp.com/feed"
    # Feel free to add more targeted feeds here
]

def fetch_recent_articles(feeds=MOCK_FEEDS, hours_ago=2):
    """
    Fetches articles from a list of RSS feeds that were published within the last `hours_ago`.
    """
    recent_articles = []
    cutoff_time = datetime.now() - timedelta(hours=hours_ago)

    for feed_url in feeds:
        logger.info(f"Parsing feed: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                # Handle varying date formats in RSS
                try:
                    if hasattr(entry, 'published_parsed'):
                        pub_tuple = entry.published_parsed
                    elif hasattr(entry, 'updated_parsed'):
                        pub_tuple = entry.updated_parsed
                    else:
                        continue # Skip if no date found
                    
                    if not pub_tuple: continue
                    
                    pub_date = datetime.fromtimestamp(time.mktime(pub_tuple))
                    
                    if pub_date >= cutoff_time:
                        article_data = {
                            'title': entry.title,
                            'url': entry.link,
                            'published_at': pub_date,
                            'source': feed_url
                        }
                        recent_articles.append(article_data)
                except Exception as e:
                    logger.debug(f"Error parsing date for entry {getattr(entry, 'title', 'Unknown')}: {e}")
                    
        except Exception as e:
            logger.error(f"Error fetching feed {feed_url}: {e}")

    return recent_articles

def scrape_article_text(url):
    """
    Downloads and parses the main text content of an article URL.
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.title, article.text
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
        return None, None

if __name__ == "__main__":
    # Quick test
    articles = fetch_recent_articles(hours_ago=24)
    print(f"Found {len(articles)} recent articles.")
    if articles:
        sample_url = articles[0]['url']
        print(f"Scraping sample: {sample_url}")
        title, text = scrape_article_text(sample_url)
        if text:
            print(f"Title: {title}")
            print(f"Preview: {text[:200]}...")
