import requests
import feedparser
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_hacker_news(top_n=10):
    """
    Fetches the top stories currently breaking on Hacker News.
    Uses the free Firebase HN API (no keys required).
    """
    logger.info("Checking Hacker News for breaking stories...")
    
    hn_top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    breaking_stories = []
    
    try:
        response = requests.get(hn_top_stories_url, timeout=5)
        if response.status_code == 200:
            story_ids = response.json()[:top_n]
            
            for story_id in story_ids:
                story_url = f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                story_data = requests.get(story_url, timeout=5).json()
                
                if story_data and 'title' in story_data:
                    breaking_stories.append({
                        'title': story_data['title'],
                        'source': 'Hacker News',
                        'score': story_data.get('score', 0),
                        'url': story_data.get('url', f"https://news.ycombinator.com/item?id={story_id}")
                    })
    except Exception as e:
        logger.error(f"Failed to fetch Hacker News: {e}")
        
    return breaking_stories

def check_reddit_rss(subreddits=['technology', 'singularity', 'artificial'], hours=2):
    """
    Parses public Reddit RSS feeds to find rising threads without using PRAW/API keys.
    """
    logger.info("Checking Reddit RSS feeds for rising threads...")
    rising_threads = []
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    for sub in subreddits:
        rss_url = f"https://www.reddit.com/r/{sub}/hot.rss"
        try:
            # feedparser can't inject headers easily, so we use requests to get the XML first
            resp = requests.get(rss_url, headers=headers, timeout=5)
            if resp.status_code != 200:
                continue
                
            feed = feedparser.parse(resp.content)
            
            for entry in feed.entries:
                if hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                    import time
                    pub_date = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                    
                    if pub_date >= cutoff_time:
                        rising_threads.append({
                            'title': entry.title,
                            'source': f'r/{sub} (RSS)',
                            'score': 'N/A (RSS)', # RSS doesn't expose live upvotes easily
                            'url': entry.link
                        })
        except Exception as e:
            logger.error(f"Failed fetching RSS for r/{sub}: {e}")
            
    return rising_threads

if __name__ == "__main__":
    hn = check_hacker_news(3)
    rd = check_reddit_rss(['programming'], hours=1)
    
    print("Test HN:", hn)
    print("Test Reddit:", rd)
