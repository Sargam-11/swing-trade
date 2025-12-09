import schedule
import time
import logging
from datetime import datetime
import config
from scoring_engine import run_daily_analysis

logging.basicConfig(
    level=config.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def daily_analysis_job():
    """Job to run daily stock analysis"""
    logger.info("="*60)
    logger.info("Starting scheduled daily analysis")
    logger.info("="*60)

    try:
        results = run_daily_analysis(config.STOCK_UNIVERSE, save_to_db=True)

        logger.info(f"Analysis completed successfully")
        logger.info(f"Buy recommendations: {len(results['buy_recommendations'])}")
        logger.info(f"Sell recommendations: {len(results['sell_recommendations'])}")

        # Log top 3 buy recommendations
        if results['buy_recommendations']:
            logger.info("\nTop Buy Recommendations:")
            for i, rec in enumerate(results['buy_recommendations'][:3], 1):
                logger.info(f"{i}. {rec['symbol']} - Score: {rec['overall_score']:.1f} - "
                          f"{rec['recommendation']}")

        # Log sell recommendations
        if results['sell_recommendations']:
            logger.info("\nSell Recommendations:")
            for rec in results['sell_recommendations']:
                logger.info(f"- {rec['symbol']} - Score: {rec['overall_score']:.1f} - "
                          f"{rec['recommendation']}")

    except Exception as e:
        logger.error(f"Error during scheduled analysis: {e}", exc_info=True)

    logger.info("="*60)
    logger.info("Scheduled analysis completed")
    logger.info("="*60)


def setup_scheduler():
    """
    Set up the daily scheduler

    Schedule analysis to run at 5:30 PM ET (after market close at 4:00 PM + 1.5 hours)
    This allows time for all data to be updated by providers
    """
    # Schedule for weekdays only (Monday-Friday)
    schedule.every().monday.at("17:30").do(daily_analysis_job)
    schedule.every().tuesday.at("17:30").do(daily_analysis_job)
    schedule.every().wednesday.at("17:30").do(daily_analysis_job)
    schedule.every().thursday.at("17:30").do(daily_analysis_job)
    schedule.every().friday.at("17:30").do(daily_analysis_job)

    logger.info("Scheduler configured - Analysis will run weekdays at 5:30 PM ET")


def run_scheduler():
    """Run the scheduler loop"""
    setup_scheduler()

    logger.info("Scheduler started. Press Ctrl+C to stop.")
    logger.info(f"Next scheduled run: {schedule.next_run()}")

    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

            # Log next run time every hour
            if datetime.now().minute == 0:
                logger.info(f"Scheduler active. Next run: {schedule.next_run()}")

    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")


def run_now():
    """Run analysis immediately (for testing)"""
    logger.info("Running analysis immediately...")
    daily_analysis_job()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "now":
        # Run analysis immediately
        run_now()
    else:
        # Start scheduler
        run_scheduler()
