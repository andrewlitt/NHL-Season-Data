# NHL-Season-Data
A script for scraping the NHL API for your favorite team's stats for a given season!

Big credits to Drew Hynes for creating the official unofficial documentation of the NHL API: https://gitlab.com/dword4/nhlapi

Created for pulling data into a Django app, visualizing data scraped from the NHL API for the Toronto Maple Leafs 2018-2019 regular season.

https://goleafsgo.herokuapp.com/

Running:
```
pip install -r requirements.txt
python game_scrape.py
```

Script Parameters:
```python
season = "2018" # pulls from the 2018-2019 season
team_id = 10 # team ID for the Leafs in the NHL API
```

Currently pulls core data for games and plays. Stores outputs as .json files and .csv's.
