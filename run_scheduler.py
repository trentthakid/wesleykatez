import schedule
import time
import logging
from scraper import scrape_property_finder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def job():
    """The job to be run by the scheduler."""
    logging.info("Scheduler is running the web scraping job...")
    try:
        scrape_property_finder()
        logging.info("Web scraping job finished successfully.")
    except Exception as e:
        logging.error(f"An error occurred during the scheduled scraping job: {e}")

# --- Schedule the Job ---
# You can change the schedule to fit your needs.
# Examples:
# schedule.every().hour.do(job)
# schedule.every().day.at("03:00").do(job)  # Run every day at 3 AM
# schedule.every(5).to(10).minutes.do(job)

# For this example, we will schedule it to run once every day.
schedule.every().day.at("03:00").do(job)

logging.info("Scheduler started. The scraping job is scheduled to run every day at 3:00 AM.")
logging.info("To run the scheduler, execute this script: python run_scheduler.py")
logging.info("Press Ctrl+C to exit the scheduler.")

# --- Run the Scheduler Loop ---
while True:
    schedule.run_pending()
    time.sleep(1)
