import os
import logging

# SETUP THE LOGGER
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=f'\033[90;1m%(levelname)s \033[0m| \033[90;1m%(funcName)s \033[0m| %(message)s')

def pretty_time(seconds):
    # Define the time intervals
    minute = 60
    hour = 3600
    day = 86400
    year = 31536000

    if seconds < minute:
        return f"{seconds}s"
    elif seconds < hour:
        return f"{seconds // minute}m {seconds % minute}s"
    elif seconds < day:
        return f"{seconds // hour}h {(seconds % hour) // minute}m {seconds % minute}s"
    elif seconds < year:
        return f"{seconds // day}d {(seconds % day) // hour}h {(seconds % hour) // minute}m {seconds % minute}s"
    else:
        return f"{seconds // year}y {(seconds % year) // day}d {(seconds % day) // hour}h {(seconds % hour) // minute}m {seconds % minute}s"


if __name__ == "__main__":
    logger.info("Starting MMDB Fabricator")

    delay = os.getenv("DELAY")
    if not delay:
        raise Exception("DELAY is not set")
    delay = int(delay)

    database_path = os.getenv("DATABASE_PATH")
    if not database_path:
        raise Exception("DATABASE_PATH is not set")
    if not database_path.endswith(".mmdb"):
        raise Exception("DATABASE_PATH must end with .mmdb")
    if not os.path.exists(os.path.dirname(database_path)):
        raise Exception("The directory of DATABASE_PATH does not exist")

    pretty_delay = pretty_time(delay)

    logger.info("Loaded the following configurations from the environment:")
    logger.info(f"DELAY: {delay} ({pretty_delay})")
    logger.info(f"DATABASE_PATH: {database_path}")

    while True:
        logger.info("Creating new MMDB file...")
        try:
            os.system(f"python create_mmdb.py {database_path}")
            logger.info("MMDB file created successfully")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        logger.info(f"Sleeping for {pretty_delay} 😴")
        time.sleep(delay)