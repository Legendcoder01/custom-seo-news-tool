from pytrends.request import TrendReq
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize pytrends
pytrends = TrendReq(hl='en-US', tz=360, retries=3, backoff_factor=1)

def validate_trend_velocity(keywords, timeframe='now 4-H'):
    """
    Validates keywords and calculates 'Interest Velocity' (how fast a topic is growing).
    Returns a dict with velocity score and a 'breakout' flag.
    """
    if not keywords:
        return {}
        
    batch_size = 5
    results = {}
    
    for i in range(0, len(keywords), batch_size):
        batch = keywords[i:i+batch_size]
        logger.info(f"Checking Trends Velocity for batch: {batch}")
        try:
            pytrends.build_payload(batch, cat=0, timeframe=timeframe, geo='', gprop='')
            df = pytrends.interest_over_time()
            
            if df.empty:
                logger.debug("No trend data found for batch.")
                for kw in batch:
                    results[kw] = {'velocity': 0, 'is_breakout': False}
                continue
                
            for kw in batch:
                if kw in df.columns:
                    # Calculate velocity: difference between recent mean and very latest
                    recent_points = df[kw].tail(3).values
                    older_points = df[kw].head(3).values
                    
                    recent_avg = sum(recent_points) / len(recent_points) if len(recent_points) else 0
                    older_avg = sum(older_points) / len(older_points) if len(older_points) else 0
                    
                    # Prevent div by zero
                    if older_avg == 0 and recent_avg > 10:
                        velocity = 5000 # Mocking a "Breakout" like Google does
                    elif older_avg == 0:
                        velocity = 0
                    else:
                        velocity = ((recent_avg - older_avg) / older_avg) * 100
                        
                    is_breakout = velocity > 1000 # If growth is >1000%, flag it
                    
                    results[kw] = {
                        'velocity': round(velocity, 2),
                        'is_breakout': is_breakout,
                        'latest_score': recent_points[-1] if len(recent_points) else 0
                    }
                else:
                    results[kw] = {'velocity': 0, 'is_breakout': False, 'latest_score': 0}
                    
            time.sleep(2) # rate limit safety
            
        except Exception as e:
            logger.error(f"Pytrends error: {e}")
            for kw in batch:
                results[kw] = {'velocity': 0, 'is_breakout': False, 'latest_score': 0}
            time.sleep(5)
            
    return results

if __name__ == "__main__":
    from pprint import pprint
    pprint(validate_trend_velocity(["OpenAI", "Sora 2", "Python"]))
