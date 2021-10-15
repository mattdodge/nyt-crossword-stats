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

### Login Issues
* If you are experiencing 403 errors and you are sure your username and password are correct, you may need to provide your login cookie normally. Follow the [instruction steps here](https://xwstats.com/link) to get your cookie, then pass it as the `NYT_COOKIE` environment variable. For example:
```
NYT_COOKIE='1ELEHES...yDo40' python fetch_puzzle_stats.py -s '2019-01-01'
```
* If your e-mail or password have some unusual characters, be sure to escape them properly, or wrap the password in quotes (`'` or `"`).

The resulting CSV file (`data.csv` by default, override with `-o` flag) has your solve stats.

## Data Format

### Example CSV:
(my real stats...don't judge me you pros out there...)
```csv
date,day,elapsed_seconds,solved,checked,revealed,streak_eligible
2019-02-14,Thu,2107,1,0,0,1
2019-02-15,Fri,2070,1,1,1,0
2019-02-16,Sat,2365,1,0,0,1
2019-02-17,Sun,0,0,0,0,0
```

date | day | elapsed_seconds | solved | checked | revealed | streak_eligible
--- | --- | --- | --- | --- | --- | ---
2019-02-14|Thu|2107|1|0|0|1
2019-02-15|Fri|2070|1|1|1|0
2019-02-16|Sat|2365|1|0|0|1
2019-02-17|Sun|0|0|0|0|0


### Fields in CSV:
* **date** - The date the puzzle was published
* **day** - The day the puzzle was published (e.g., "Mon", "Tue") - useful for comparing different difficulties
* **elapsed** - How long it took you to solve the puzzle, in seconds
* **solved** - `1` if you finished/solved the puzzle, `0` otherwise
* **checked** - `1` if you had to check an answer on the puzzle, thus making it ineligible for streaks
* **revealed** - `1` if you had to reveal an answer on the puzzle, thus making it ineligible for streaks
* **streak_eligible** - `1` if the puzzle counts towards your NYT streak - this means you solved without cheating (checks or reveals) on the day of the puzzle before Midnight PST

## Example

For an example of how to use this data, I plotted my solve times over the last ~8 months, grouped by day:
![example chart](example_chart.png)
