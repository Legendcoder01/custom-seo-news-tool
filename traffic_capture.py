import logging
import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_keyword_traffic_metrics(keyword):
    """
    Mock function simulating Ahrefs/SEMrush and a SERP API (like Serpstack).
    Returns Volume, Difficulty, and Number of Search Results.
    """
    seed = len(keyword) * sum([ord(c) for c in keyword])
    random.seed(seed)
    
    # Simulating the Zero-Volume filter. Sometimes hot breaking news has 0 volume in standard tools.
    volume = random.choice([0, 0, 150, 500, 2000, 50000])
    
    return {
        'estimated_volume': volume,
        'keyword_difficulty': random.randint(1, 95),
        'total_search_results': random.randint(500, 5000000) # For competition
    }

def calculate_capture_index(trend_data, metrics):
    """
    Calculates the Capture Index (CI).
    CI = (Interest_Velocity * Estimated_Volume) / Keyword_Difficulty
    """
    velocity = trend_data.get('velocity', 0)
    
    # If volume is 0 but it's a breakout, we assign a massive pseudo-volume 
    # because standard SEO tools are lagging behind reality.
    vol = metrics.get('estimated_volume', 0)
    if vol == 0 and trend_data.get('is_breakout'):
        vol = 10000 # Correcting zero-volume lag
        
    kd = metrics.get('keyword_difficulty', 1)
    if kd == 0: kd = 1
    
    # Basic math handling for negative drops in interest
    if velocity < 0:
        return 0
        
    ci = (velocity * vol) / kd
    return round(ci, 2)

def evaluate_opportunity(keyword, trend_data):
    """
    Orchestrates metrics fetching, CI scoring, and flagging.
    """
    metrics = get_keyword_traffic_metrics(keyword)
    ci_score = calculate_capture_index(trend_data, metrics)
    
    flags = []
    
    # Rule 1: Zero-Volume Filter
    if metrics['estimated_volume'] == 0 and trend_data.get('is_breakout'):
        flags.append("GOLDEN OPPORTUNITY (Zero Volume Breakout)")
        
    # Rule 2: Instant Rank (Low competition + Breakout)
    if metrics['total_search_results'] < 10000 and trend_data.get('is_breakout'):
        flags.append("INSTANT RANK (Low SERP Competition)")
        
    return {
        'keyword': keyword,
        'capture_index': ci_score,
        'flags': flags,
        'velocity': trend_data.get('velocity', 0),
        'metrics': metrics
    }
