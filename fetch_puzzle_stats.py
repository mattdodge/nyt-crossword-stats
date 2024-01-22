import argparse
import os
import pickle
from csv import DictWriter
from datetime import datetime, timedelta
import time

import requests
from dotenv import load_dotenv
from tqdm import tqdm

load_dotenv()

API_ROOT = "http://www.nytimes.com/svc/crosswords"
PUZZLE_INFO = API_ROOT + "/v3/puzzles.json"
PUZZLE_DETAIL = API_ROOT + "/v6/game/"

DATE_FORMAT = "%Y-%m-%d"

parser = argparse.ArgumentParser(description="Fetch NYT Crossword stats")
parser.add_argument("-u", "--username", help="NYT Account Email Address")
parser.add_argument("-p", "--password", help="NYT Account Password")
parser.add_argument(
    "-s",
    "--start-date",
    help="The first date to pull from, inclusive (defaults to 30 days ago)",
    default=datetime.strftime(datetime.now() - timedelta(days=30), DATE_FORMAT),
)
parser.add_argument(
    "-e",
    "--end-date",
    help="The last date to pull from, inclusive (defaults to today)",
    default=datetime.strftime(datetime.now(), DATE_FORMAT),
)
parser.add_argument(
    "-o", "--output-csv", help="The CSV file to write to", default="data.csv"
)
parser.add_argument(
    "-t",
    "--type",
    help='The type of puzzle data to fetch. Valid values are "daily", "bonus", and "mini" (defaults to daily)',
    default="daily",
)


def login(username, password):
    """Return the NYT-S cookie after logging in"""
    login_resp = requests.post(
        "https://myaccount.nytimes.com/svc/ios/v2/login",
        data={
            "login": username,
            "password": password,
        },
        headers={
            "User-Agent": "Crosswords/20191213190708 CFNetwork/1128.0.1 Darwin/19.6.0",
            "client_id": "ios.crosswords",
        },
    )
    login_resp.raise_for_status()
    for cookie in login_resp.json()["data"]["cookies"]:
        if cookie["name"] == "NYT-S":
            return cookie["cipheredValue"]
    raise ValueError("NYT-S cookie not found")


def get_v3_puzzle_overview(puzzle_type, start_date, end_date, cookie):
    payload = {
        "publish_type": puzzle_type,
        "sort_order": "asc",
        "sort_by": "print_date",
        "date_start": start_date.strftime("%Y-%m-%d"),
        "date_end": end_date.strftime("%Y-%m-%d"),
    }

    overview_resp = requests.get(PUZZLE_INFO, params=payload, cookies={"NYT-S": cookie})

    overview_resp.raise_for_status()
    puzzle_info = overview_resp.json().get("results")
    return puzzle_info


def get_v3_puzzle_detail(puzzle_id, cookie):
    puzzle_resp = requests.get(
        f"{PUZZLE_DETAIL}/{puzzle_id}.json", cookies={"NYT-S": cookie}
    )

    puzzle_resp.raise_for_status()
    puzzle_detail = puzzle_resp.json()["calcs"]

    # crude rate limiting
    time.sleep(0.25)
    return puzzle_detail


if __name__ == "__main__":
    args = parser.parse_args()
    cookie = os.getenv("NYT_COOKIE")
    if not cookie:
        cookie = login(args.username, args.password)

    start_date = datetime.strptime(args.start_date, DATE_FORMAT)
    end_date = datetime.strptime(args.end_date, DATE_FORMAT)

    days_between = (end_date - start_date).days
    batches = (days_between // 100) + 1

    print(
        f"Getting stats from {args.start_date} until {args.end_date} in {batches} batches"
    )

    date = start_date

    if end_date - start_date > timedelta(days=100):
        batch_end = start_date + timedelta(days=100)
    else:
        batch_end = end_date
    batch_start = start_date

    puzzle_overview = []

    for batch in (pbar := tqdm(range(batches))):
        pbar.set_description(f"Start date: {batch_start}")
        batch_overview = get_v3_puzzle_overview(
            puzzle_type=args.type,
            start_date=batch_start,
            end_date=batch_end,
            cookie=cookie,
        )
        puzzle_overview.extend(batch_overview)
        batch_start = batch_start + timedelta(days=100)
        batch_end = batch_end + timedelta(days=100)

    # A temporary file just in case it dies with those solve times
    with open("tmp.pkl", "wb") as f:
        pickle.dump(puzzle_overview, f)

    print("\nGetting puzzle solve times\n")

    for puzzle in tqdm(puzzle_overview):
        detail = get_v3_puzzle_detail(puzzle_id=puzzle["puzzle_id"], cookie=cookie)
        puzzle["solving_seconds"] = detail.get("secondsSpentSolving", None)
        puzzle["day_of_week_name"] = datetime.strptime(puzzle["print_date"], DATE_FORMAT).strftime('%A')
        puzzle["day_of_week_integer"] = datetime.strptime(puzzle["print_date"], DATE_FORMAT).strftime('%w')

    fields = [
        "author",
        "editor",
        "format_type",
        "print_date",
        "day_of_week_name",
        "day_of_week_integer",
        "publish_type",
        "puzzle_id",
        "title",
        "version",
        "percent_filled",
        "solved",
        "star",
        "solving_seconds",
    ]

    print("Writing stats to {}".format(args.output_csv))

    with open(args.output_csv, "w") as f:
        writer = DictWriter(f, fields)
        writer.writeheader()
        writer.writerows(puzzle_overview)

    os.remove("tmp.pkl")
    print("{} rows written to {}".format(len(puzzle_overview), args.output_csv))
