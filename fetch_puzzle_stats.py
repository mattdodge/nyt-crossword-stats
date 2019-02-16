import argparse
from csv import DictWriter
from datetime import datetime, timedelta
import requests
from tqdm import tqdm

API_ROOT = 'https://nyt-games-prd.appspot.com/svc/crosswords'
PUZZLE_INFO = API_ROOT + '/v2/puzzle/daily-{date}.json'
SOLVE_INFO = API_ROOT + '/v2/game/{game_id}.json'
DATE_FORMAT = '%Y-%m-%d'

parser = argparse.ArgumentParser(description='Fetch NYT Crossword stats')
parser.add_argument(
    '-u', '--username', help='NYT Account Email Address', required=True)
parser.add_argument(
    '-p', '--password', help='NYT Account Password', required=True)
parser.add_argument(
    '-s', '--start-date',
    help='The first date to pull from, inclusive (defaults to 30 days ago)',
    default=datetime.strftime(datetime.now() - timedelta(days=30), DATE_FORMAT)
)
parser.add_argument(
    '-e', '--end-date',
    help='The last date to pull from, inclusive (defaults to today)',
    default=datetime.strftime(datetime.now(), DATE_FORMAT)
)
parser.add_argument(
    '-o', '--output-csv',
    help='The CSV file to write to',
    default='data.csv'
)
parser.add_argument(
    '--strict',
    help='Don\'t allow missing puzzles or errors',
    action='store_true',
)


def login(username, password):
    """ Return the NYT-S cookie after logging in """
    login_resp = requests.post(
        'https://myaccount.nytimes.com/svc/ios/v2/login',
        data={
            'login': username,
            'password': password,
        },
        headers={
            'client_id': 'ios.crosswords',
        }
    )
    login_resp.raise_for_status()
    for cookie in login_resp.json()['data']['cookies']:
        if cookie['name'] == 'NYT-S':
            return cookie['cipheredValue']
    raise ValueError('NYT-S cookie not found')


def get_puzzle_stats(date, cookie):
    puzzle_resp = requests.get(
        PUZZLE_INFO.format(date=date),
        cookies={
            'NYT-S': cookie,
        },
    )
    puzzle_resp.raise_for_status()
    puzzle_info = puzzle_resp.json().get('results')[0]
    solve_resp = requests.get(
        SOLVE_INFO.format(game_id=puzzle_info['puzzle_id']),
        cookies={
            'NYT-S': cookie,
        },
    )
    solve_resp.raise_for_status()
    solve_info = solve_resp.json().get('results')
    return solve_info


def format_solve_info(solve_info):
    return {
        'elapsed_seconds': solve_info.get('timeElapsed', 0),
        'solved': int(solve_info.get('solved', False)),
        'checked': int('firstChecked' in solve_info),
        'revealed': int('firstRevealed' in solve_info),
    }


if __name__ == '__main__':
    args = parser.parse_args()
    cookie = login(args.username, args.password)
    start_date = datetime.strptime(args.start_date, DATE_FORMAT)
    end_date = datetime.strptime(args.end_date, DATE_FORMAT)
    print("Getting stats from {} until {}".format(
        datetime.strftime(start_date, DATE_FORMAT),
        datetime.strftime(end_date, DATE_FORMAT)))
    date = start_date
    fields = [
        'date',
        'day',
        'elapsed_seconds',
        'solved',
        'checked',
        'revealed',
    ]
    with open(args.output_csv, 'w') as csvfile, \
            tqdm(total=(end_date-start_date).days + 1) as pbar:
        writer = DictWriter(csvfile, fields)
        writer.writeheader()
        count = 0
        while date <= end_date:
            date_str = datetime.strftime(date, DATE_FORMAT)
            try:
                solve = format_solve_info(get_puzzle_stats(date_str, cookie))
                solve['date'] = date_str
                solve['day'] = datetime.strftime(date, '%a')
                writer.writerow(solve)
                count += 1
            except Exception:
                # Ignore missing puzzles errors in non-strict
                if args.strict:
                    raise
            pbar.update(1)
            date += timedelta(days=1)

    print("{} rows written to {}".format(count, args.output_csv))
