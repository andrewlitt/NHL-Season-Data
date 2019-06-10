import json
import csv
import os
import requests

# SCRIPT VARIABLES
season = "2018"
team_id = 10

# Make storage directory
data = json.loads(requests.get('https://statsapi.web.nhl.com/api/v1/teams/'+str(team_id)).content)
teamName = data["teams"][0]["name"]
path = season + ' ' + teamName+' Stats'
if not os.path.exists(path):
    os.makedirs(path)
print('Beginning scape of the '+season+' season for the '+ teamName)
# Init CSV's for writing
game_csv = open(os.path.join(path, 'game.csv'),'a+',newline='')
game_plays_csv = open(os.path.join(path, 'game_plays.csv'),'a+',newline='')
game_plays_players_csv = open(os.path.join(path, 'game_plays_players.csv'),'a+',newline='')
game_shifts_csv = open(os.path.join(path, 'game_shifts.csv'),'a+',newline='')
game_teams_stats_csv  = open(os.path.join(path, 'game_teams_stats.csv'),'a+',newline='')

game_csvwriter = csv.writer(game_csv)
game_plays_csvwriter = csv.writer(game_plays_csv)
game_plays_players_csvwriter = csv.writer(game_plays_players_csv)
game_shifts_csvwriter =  csv.writer(game_shifts_csv)
game_teams_stats_csvwriter = csv.writer(game_teams_stats_csv)

game_json= open(os.path.join(path, 'game.json'),'a+',newline='')
game_plays_json = open(os.path.join(path, 'game_plays.json'),'a+',newline='')
game_plays_players_json = open(os.path.join(path, 'game_plays_players.json'),'a+',newline='')
# game_shifts_json = open(os.path.join(path, 'game_shifts.json'),'a+',newline='')
# game_teams_stats_json  = open(os.path.join(path, 'game_teams_stats.json'),'a+',newline='')

# Get all buds games for the season
leafs_games = []
num = 1
while True:
    strpad = ""
    if num < 1000:
        strpad = "0"
        if num < 100:
            strpad = "00"
            if num < 10:
                strpad = "000"
    strnum = strpad + str(num)
    url = "https://statsapi.web.nhl.com/api/v1/game/"+str(season)+"02"+strnum+"/linescore"
    print('Checking Game: '+strnum+'/1271')
    data = json.loads(requests.get(url).content)
    if "message" in data:
        break
    if data["teams"]["away"]["team"]["id"] == team_id  or data["teams"]["home"]["team"]["id"] == team_id:
        leafs_games.append(str(season)+"02"+strnum)
    num += 1

print('Complete!')
game_json.write('[')
game_plays_json.write('[')
game_plays_players_json.write('[')
# game_shifts_json.write('[')
# game_teams_stats_json .write('[')

play_entry_no = 1
# Retrieve stats for each buds game
lastgame = len(leafs_games)-1
for game_num, gamePk in enumerate(leafs_games):
    print('Scraping Game: '+ str(game_num+1))
    url = "https://statsapi.web.nhl.com/api/v1/game/" + str(leafs_games[game_num]) + "/feed/live"
    data = json.loads(requests.get(url).content)

    # Load Game Data
    game_id = data["gameData"]["game"]["pk"]
    season = data["gameData"]["game"]["season"]
    game_type = data["gameData"]["game"]["type"]
    date_time = data["gameData"]["datetime"]["dateTime"]
    game_length = data["liveData"]["linescore"]["currentPeriod"]
    away_id = data["gameData"]["teams"]["away"]["id"]
    home_id = data["gameData"]["teams"]["home"]["id"]
    away_goals = data["liveData"]["linescore"]["teams"]["away"]["goals"]
    home_goals = data["liveData"]["linescore"]["teams"]["home"]["goals"]
    home_rink_side_start = "NA"
    if "rinkSide" in data["liveData"]["linescore"]["periods"][0]["home"]:
        home_rink_side_start = data["liveData"]["linescore"]["periods"][0]["home"]["rinkSide"]

    # Generate outcome string
    winTeam = "home"
    homeWin = True
    if away_goals > home_goals:
        winTeam = "away"
        homeWin = False
    gameLen = "REG"
    if game_length == 4:
        gameLen = "OT"
    outcome = winTeam + " win " + gameLen

    # Game entry item
    game_entry = [
        game_id,
        season,
        game_type,
        date_time,
        away_id,
        home_id,
        away_goals,
        home_goals,
        outcome,
        home_rink_side_start,
        data["gameData"]["venue"]["name"]
    ]
    game_csvwriter.writerow(game_entry)
    game_entry = ({
        'model': 'gamedata.game',
        'pk': game_num,
        'fields':{
            'game_id': game_id,
            'season': season,
            'type': game_type,
            'date_time': date_time,
            'away_team_id': away_id,
            'home_team_id': home_id,
            'away_goals': away_goals,
            'home_goals': home_goals,
            'outcome': outcome,
            'home_rink_side_start': home_rink_side_start,
            'venue': data["gameData"]["venue"]["name"]
        }
    })
    json.dump(game_entry, game_json)

    home_stats = data["liveData"]["boxscore"]["teams"]["home"]["teamStats"]["teamSkaterStats"]
    away_stats = data["liveData"]["boxscore"]["teams"]["away"]["teamStats"]["teamSkaterStats"]

    game_home_teams_stats_entry = [
        game_id,
        home_id,
        'home',
        homeWin,
        gameLen,
        data["liveData"]["boxscore"]["teams"]["home"]["coaches"][0]["person"]["fullName"],
        home_stats["goals"],
        home_stats["shots"],
        home_stats["hits"],
        home_stats["pim"],
        home_stats["powerPlayOpportunities"],
        home_stats["powerPlayGoals"],
        home_stats["faceOffWinPercentage"],
        home_stats["giveaways"],
        home_stats["takeaways"],
        home_stats["blocked"]
    ]
    game_teams_stats_csvwriter.writerow(game_home_teams_stats_entry)

    game_away_teams_stats_entry = [
        game_id,
        away_id,
        'away',
        not homeWin,
        gameLen,
        data["liveData"]["boxscore"]["teams"]["away"]["coaches"][0]["person"]["fullName"],
        away_stats["goals"],
        away_stats["shots"],
        away_stats["hits"],
        away_stats["pim"],
        away_stats["powerPlayOpportunities"],
        away_stats["powerPlayGoals"],
        away_stats["faceOffWinPercentage"],
        away_stats["giveaways"],
        away_stats["takeaways"],
        away_stats["blocked"]
    ]
    game_teams_stats_csvwriter.writerow(game_away_teams_stats_entry)

    lastplay = len(data["liveData"]["plays"]["allPlays"]) - 1

    for play_num, play in enumerate(data["liveData"]["plays"]["allPlays"]):
        # Parse Play ID
        play_id = str(game_id) + '_' + str(play_num)
        # Team_ID's
        team_id_for = '-1'
        team_id_against = '-1'
        if "team" in play:
            team_id_for = play["team"]["id"]
            if team_id_for == home_id:
                team_id_against = away_id
            else:
                team_id_against = home_id
        # event & secondaryType
        event = play["result"]["event"]
        secondaryType = "NA"
        if "secondaryType" in play["result"]:
            secondaryType = play["result"]["secondaryType"]

        # xy and st_xy logic
        period = play["about"]["period"]
        x = "-1"
        y = "-1"
        st_x = "-1"
        st_y = "-1"

        if "x" in play["coordinates"]:
            x = play["coordinates"]["x"]
            y = play["coordinates"]["y"]

            flip = False

            if home_rink_side_start == 'right':
                flip = True
            if period % 2 == 0:
                flip = not flip
            if flip:
                st_x = -x
                st_y = -y
            else:
                st_x = x
                st_y = y

        # Load Object
        game_play_entry = [
            play_id,
            game_id,
            play_num,
            team_id_for,
            team_id_against,
            event,
            secondaryType,
            x,
            y,
            period,
            play["about"]["periodType"],
            play["about"]["periodTime"],
            play["about"]["periodTimeRemaining"],
            play["about"]["dateTime"],
            play["about"]["goals"]["away"],
            play["about"]["goals"]["home"],
            play["result"]["description"],
            st_x,
            st_y,
        ]
        game_plays_csvwriter.writerow(game_play_entry)
        game_play_entry = ({
            'model': 'gamedata.game_plays',
            'pk': play_entry_no,
            'fields':{
                'play_id': play_id,
            	'game_id': game_id,
            	'play_num': play_num,
            	'team_id_for': team_id_for,
            	'team_id_against': team_id_against,
            	'event': event,
            	'secondaryType': secondaryType,
            	'x': x,
            	'y': y,
            	'period': period,
            	'periodType': play["about"]["periodType"],
            	'periodTime': play["about"]["periodTime"],
            	'periodTimeRemaining': play["about"]["periodTimeRemaining"],
            	'dateTime': play["about"]["dateTime"],
            	'goals_away': play["about"]["goals"]["away"],
            	'goals_home': play["about"]["goals"]["home"],
            	'description': play["result"]["description"],
            	'st_x': st_x,
            	'st_y': st_y
            }
        })
        json.dump(game_play_entry, game_plays_json)
        play_entry_no +=1
        if "players" in play:
            lastplayer = len(play["players"])-1
            for player_num, player in enumerate(play["players"]):
                game_play_players = [
                    play_id,
                    game_id,
                    play_num,
                    player["player"]["id"],
                    player["playerType"]
                ]
                game_plays_players_csvwriter.writerow(game_play_players)
                game_play_players = ({
                    'model': 'gamedata.game_plays_players',
                    'pk': play_id,
                    'fields':{
                        'play_id': play_id,
                    	'game_id': game_id,
                    	'play_num': play_num,
                        'player_id': player["player"]["id"],
                        'player_type': player["playerType"]
                    }
                })
                json.dump(game_play_players, game_plays_players_json)
                if player_num != lastplayer:
                        game_plays_players_json.write(',')
        if play_num != lastplay:
            game_plays_json.write(',')
            if "players" in play:
                game_plays_players_json.write(',')

    if game_num != lastgame:
        game_json.write(',')
        game_plays_json.write(',')
        if "players" in play:
            game_plays_players_json.write(',')

    shifturl = "http://www.nhl.com/stats/rest/shiftcharts?cayenneExp=gameId=" + str(game_id)
    shiftdata = json.loads(requests.get(shifturl).content)
    for shift in shiftdata["data"]:
        shift_entry = [
            game_id,
            shift["playerId"],
            shift["period"],
            shift["duration"],
            shift["startTime"],
            shift["endTime"]
        ]
        game_shifts_csvwriter.writerow(shift_entry)

# Add csv writes
game_json.write(']')
game_plays_json.write(']')
game_plays_players_json.write(']')
# game_shifts_json.write(']')
# game_teams_stats_json .write(']')

game_json.close()
game_plays_json.close()
game_plays_players_json.close()
# game_shifts_json.close()
# game_teams_stats_json.close()

# Close files
game_csv.close()
game_plays_csv.close()
game_plays_players_csv.close()
game_shifts_csv.close()
game_teams_stats_csv.close()
