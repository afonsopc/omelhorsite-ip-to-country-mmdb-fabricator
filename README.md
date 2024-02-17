# omelhorsite-ip-to-country-mmdb-fabricator

This application and creates a MMDB that is used to find the country of an IP address.

## Requirements

- Python 3
- Docker (optional)

## Installation

1. Clone this repository.
2. Install the Python dependencies:

```sh
pip install -r requirements.txt
```

## Usage

You can run the script directly with Python:

```sh
DELAY=30 DATABASE_PATH=database.mmdb python create_mmdb.py
```

Or you can use Docker:

```sh
docker compose up
```

The script will run indefinitely, creating a new MMDB file every `DELAY` seconds. The `DELAY` and `DATABASE_PATH` environment variables must be set. If you're using Docker, these can be set in the `docker-compose.yml` file.

## Environment Variables

- `DELAY`: The delay, in seconds, between each creation of the MMDB file.
- `DATABASE_PATH`: The path where the MMDB file will be created.
