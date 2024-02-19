# NYT Crossword Stats

Fetch your NYT Crossword Puzzle solve stats and export them as CSV.

The NYT app shows minimal information around your streaks and average solve times. This gets you the raw data so you can do your own analysis.


## What's a GitHub?
Not well-versed in Python or the command-line? Consider signing up for [XW Stats](https://xwstats.com). It's a free site that automatically fetches your solves and allows you to download them as a CSV.

## Requirements

1. Python
2. A NYT Crossword subscription

## Installation

1. Clone this repository
2. `pip install -r requirements.txt`

## Usage

Fetch all solve stats since January 1, 2019. Use your NYT email and passwords as arguments here
```bash
python fetch_puzzle_stats.py -u your@email.com -p yourpass -s 2019-01-01
```
## Options

Follow the command `python fetch_puzzle_stats.py` with these options if you want to:
* `-u` or `--username` The email address for your NYT account
* `-p` or `--password` The password for your NYT account
* `-s` or `--start_date` The date to start fetching stats from (default: 30 days ago)
* `-e` or `--end_date` The date to stop fetching stats from (default: today)
* `-o` or `--output` The name of the CSV file to output (default: data.csv)
* `-t` or `--type` The type of puzzle to fetch. One of "daily", "mini", or "bonus" (default: Daily)

### Login Issues
If you are experiencing 403 errors and you are _sure_ your username and password are correct, you may need to provide your login cookie manually. It's a two-step process: 

1) Follow the [instruction steps here](https://xwstats.com/link) to get your cookie.
2) Rename the file `.env.template` to `.env` and paste your cookie into it like this:
```
NYT_COOKIE=1ELEHES...yDo40
```
* If your e-mail or password have some unusual characters, be sure to escape them properly, or wrap the password in quotes (`'` or `"`).

The resulting CSV file (`data.csv` by default, override with `-o` flag) has your solve stats.

## Data Format

### Example CSV:
(my real stats...don't judge me you pros out there...)
```csv
author,editor,format_type,print_date,day_of_week_name,day_of_week_integer,publish_type,puzzle_id,title,version,percent_filled,solved,star,solving_seconds
Will Nediger,Will Shortz,Normal,2023-12-23,Saturday,6,Daily,21560,,0,100,True,Gold,675
Drew Schmenner,Will Shortz,Normal,2023-12-24,Sunday,0,Daily,21568,Wrap Stars,0,100,True,Gold,1449
Amie Walker,Will Shortz,Normal,2023-12-25,Monday,1,Daily,21567,,0,100,True,Gold,243
```
| author         | editor      | format_type | print_date | day_of_week_name | day_of_week_integer | publish_type | puzzle_id | title      | version | percent_filled | solved | star | solving_seconds |
|----------------|-------------|-------------|------------|------------------|---------------------|--------------|-----------|------------|---------|----------------|--------|------|-----------------|
| Will Nediger   | Will Shortz | Normal      | 2023-12-23 | Saturday         | 6                   | Daily        | 21560     |            | 0       | 100            | True   | Gold | 675             |
| Drew Schmenner | Will Shortz | Normal      | 2023-12-24 | Sunday           | 0                   | Daily        | 21568     | Wrap Stars | 0       | 100            | True   | Gold | 1449            |
| Amie Walker    | Will Shortz | Normal      | 2023-12-25 | Monday           | 1                   | Daily        | 21567     |            | 0       | 100            | True   | Gold | 243             |




### Fields in CSV:
* **author** - The author(s) of the puzzle
* **editor** - Almost always Will Shortz
* **format_type** - Almost always "Normal"
* **print_date** - Date the puzzle was published
* **day_of_week_name** - Pretty name of the puzzle's day
* **day_of_week_integer** - Integer value, Sunday = `0`, Monday = `1` ...
* **publish_type** - `Normal`, `Mini`, `Bonus`
* **puzzle_id** - NYT's reference ID for the puzzle
* **title** - The puzzle's title (for Sundays)
* **version** - NYT's version of the puzzle
* **solved** - Whether the puzzle was solved
* **star** - Gold if solved before midnight Pacific of its date (value available starting 2018-12-12 )
* **solving_seconds** - how long it took to solve the puzzle

## Example

For an example of how to use this data, I plotted my solve times over the last ~8 months, grouped by day:
![example chart](example_chart.png)
