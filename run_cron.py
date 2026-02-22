import time
import schedule
import logging
from main import run_pipeline

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def job():
    logger.info("Executing scheduled SEO pipeline run...")
    run_pipeline()
    logger.info("Run finished. Waiting for next interval.")

if __name__ == "__main__":
    logger.info("Starting background worker for SEO pipeline.")
    
    # Run once immediately on startup
    job()
    
    # Schedule to run every 2 hours (fitting Phase A's 2-hour window request)
    schedule.every(2).hours.do(job)
    
    # Keep the worker alive and running pending tasks
    while True:
        schedule.run_pending()
        time.sleep(60)
