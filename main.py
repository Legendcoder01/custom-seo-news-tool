import sys
import logging
from collections import Counter
from urllib.parse import urlparse

# Import modules
from scraper import fetch_recent_articles, scrape_article_text
from extractor import extract_keywords
from trends import validate_trend_velocity
from traffic_capture import evaluate_opportunity
from social_monitor import check_hacker_news, check_reddit_rss
from db import db

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def phase_a_newness_sighting(hours_ago=2):
    """
    Phase A: Scrapes recent articles, extracts keywords, logs them into
    PostgreSQL memory, and detects immediate Cross-Site Alerts.
    """
    logger.info(f"--- Starting Phase A: News Ingestion & DB Memory ({hours_ago} hours) ---")
    articles = fetch_recent_articles(hours_ago=hours_ago)
    
    if not articles:
        return []

    all_keywords = []
    cross_site_alerts = set()
    
    for idx, article_meta in enumerate(articles):
        logger.info(f"Scraping [{idx+1}/{len(articles)}]: {article_meta['title']}")
        title, text = scrape_article_text(article_meta['url'])
        
        full_text = f"{title}. {text}" if text else title
        if full_text:
            kws = extract_keywords(full_text, top_n=5)
            source_domain = urlparse(article_meta['url']).netloc
            
            for kw in kws:
                all_keywords.append(kw)
                # Log to DB Memory
                db.log_sighting(kw, article_meta['url'], source_domain)
                
                # Check for High-Priority Alert (seen on >= 5 sites in last hour)
                is_alert, source_count = db.check_high_priority_alert(kw, hours=1, min_sources=3) # Changed to 3 for demo scale
                if is_alert:
                    cross_site_alerts.add((kw, source_count))

    if cross_site_alerts:
        logger.warning(f"🚨 DATABASE ALERT: Multi-site propagation detected for: {cross_site_alerts}")
                    
    # Basic frequency baseline for processing 
    kw_frequency = Counter(all_keywords)
    trending_candidates = [kw for kw, count in kw_frequency.items() if count >= 2]
    
    return trending_candidates

def phase_b_traffic_capture_score(keywords):
    """
    Phase B: High Traffic Capture Pivot
    Verifies Interest Velocity (Breakouts) and Calculates the Capture Index (CI).
    """
    logger.info("--- Starting Phase B: Capturing Interest Velocity & CI Score ---")
    if not keywords:
        return []
        
    trend_data = validate_trend_velocity(keywords)
    
    opportunities = []
    for kw in keywords:
        kw_trend = trend_data.get(kw, {})
        velocity = kw_trend.get('velocity', 0)
        
        # We process it if it has positive velocity 
        if velocity >= 0:
            opp = evaluate_opportunity(kw, kw_trend)
            opportunities.append(opp)
            
    # Sort by highest Traffic Capture Index
    opportunities.sort(key=lambda x: x['capture_index'], reverse=True)
    return opportunities

def phase_c_social_sighting():
    """
    Phase C: Intercept key-less Social APIs (HN and Reddis RSS).
    """
    logger.info("--- Starting Phase C: Key-less Social Monitors ---")
    
    hn_stories = check_hacker_news(top_n=5)
    rss_threads = check_reddit_rss(subreddits=['technology', 'artificial'], hours=2)
    
    combined = hn_stories + rss_threads
    
    social_signals = []
    for story in combined:
        kws = extract_keywords(story['title'], top_n=3)
        social_signals.append({
            'title': story['title'],
            'source': story['source'],
            'score': story['score'],
            'keywords': kws
        })
        
    return social_signals

def run_pipeline():
    logger.info("=== HIGH TRAFFIC SEO PIPELINE STARTED ===")
    
    candidate_keywords = phase_a_newness_sighting()
    traffic_opportunities = phase_b_traffic_capture_score(candidate_keywords)
    social_signals = phase_c_social_sighting()
    
    logger.info("=== PIPELINE RESULTS ===")
    
    if traffic_opportunities:
        print("\n📈 HIGH TRAFFIC CAPTURE OPPORTUNITIES 📈")
        for t in traffic_opportunities[:5]:
            print(f"- '{t['keyword']}' (CI Score: {t['capture_index']} | Velocity: {t['velocity']}%)")
            if t['flags']:
                print(f"   🚨 ALERT: {', '.join(t['flags'])}")
            print(f"   Est. Volume: {t['metrics']['estimated_volume']} | KD: {t['metrics']['keyword_difficulty']} | SERP Results: {t['metrics']['total_search_results']}")
    else:
        print("\nNo breakout traffic opportunities detected right now.")
        
    if social_signals:
        print("\n🌐 BREAKING SOCIAL SIGNALS (Hacker News + Reddit RSS) 🌐")
        for s in social_signals[:5]:
            print(f"- [{s['source']}] {s['title']} (Score: {s['score']})")
            print(f"   Keywords: {', '.join(s['keywords'])}")

if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\nPipeline stopped by user.")
        sys.exit(0)
