import netaddr
import mmdbencoder
import csv
from collections import namedtuple
import os
import time
import requests
import shutil
import gzip
import uuid
import logging

# SETUP THE LOGGER
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format=f'\033[90;1m%(levelname)s \033[0m| \033[90;1m%(funcName)s \033[0m| %(message)s')

def download_file(url: str, file_path: str):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(file_path, "wb") as out_file:
        shutil.copyfileobj(response.raw, out_file)
    del response

def decompress_file(file_path: str, out_file_path: str, remove_original: bool = False):
    with gzip.open(file_path, "rb") as f_in:
        with open(out_file_path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)
    if remove_original:
        os.remove(file_path)

def read_csv_into_encoder(encoder: mmdbencoder.Encoder, file_path: str, remove_file: bool = False):
    iso_codes = {}
    with open(file_path, newline="") as csvfile:
        csv_reader = csv.DictReader(csvfile, delimiter="\t", fieldnames=["start", "end", "as_num", "iso_code", "as_description"])
        for row in csv_reader:
            # Insert country data only once
            if row['iso_code'] in iso_codes:
                data_offset = iso_codes[row['iso_code']]
            else:
                data_offset = encoder.insert_data({"country": {"iso_code": row['iso_code']}})
                iso_codes[row['iso_code']] = data_offset

            cidrs = netaddr.iprange_to_cidrs(row['start'], row['end'])
            for cidr in cidrs:
                encoder.insert_network(cidr, data_offset, strict=False)
    if remove_file:
        os.remove(file_path)

def create_mmdb_from_encoder(encoder: mmdbencoder.Encoder, db_path: str):
    with open(db_path, "wb") as f:
        encoder.write(f)

def create_mmdb(db_path: str):
    url = "https://iptoasn.com/data/ip2asn-combined.tsv.gz"
    file_path = "ip2asn-combined.tsv.gz"
    file_path_decompressed = "ip2asn-combined.tsv"

    logger.info("Downloading file")
    download_file(url, file_path)

    logger.info("Decompressing file")
    decompress_file(file_path, file_path_decompressed, remove_original=True)

    logger.info("Creating encoder")
    enc = mmdbencoder.Encoder(
        6,  # IP version
        32,  # Size of the pointers
        "Geoacumen-Country",  # Name of the table
        ["en"],  # Languages
        {
            "en": "Geoacumen - Open Source IP to country mapping database by Kevin Chung"
        },  # Description
        compat=True,
    )

    logger.info("Reading data into encoder")
    read_csv_into_encoder(enc, file_path_decompressed, remove_file=True)

    logger.info("Writing encoder into database file")
    create_mmdb_from_encoder(enc, db_path)

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
            create_mmdb(database_path)
            logger.info("MMDB file created successfully")
        except Exception as e:
            logger.error(f"An error occurred: {e}")
        logger.info(f"Sleeping for {pretty_delay} 😴")
        time.sleep(delay)