import netaddr
import mmdbencoder
import csv
from collections import namedtuple
import sys
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

if __name__ == "__main__":
    logger.info("Starting MMDB Fabricator")

    logger.info("Getting the database path from arguments")
    database_path = sys.argv[1]

    logger.info("Creating new MMDB file...")
    try:
        create_mmdb(database_path)
        logger.info("MMDB file created successfully")
    except Exception as e:
        logger.error(f"An error occurred: {e}")