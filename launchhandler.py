import json
import logging
import speech
import urllib
import websocket

from users import USERID_TO_NAME
from users import STEAMID_TO_USERID


DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=6&encoding=json"
BOT_TOKEN = "<token>"

STEAM_PLAYER_SUMMARIES = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={}&steamids={}"
STEAM_API_KEY = "<key>"

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def handle(request):
    presences = get_guild_presences()
    presences = [presence for presence in presences if presence['game'] is not None]
    presences = [presence for presence in presences if presence['user']['id'] in USERID_TO_NAME]

    discord_games = get_discord_games(presences)
    LOG.info('discord games: ' + str(discord_games))

    summaries = get_steam_player_summaries()
    steam_games = get_steam_games(summaries)
    steam_games_with_user_id =  {game:[STEAMID_TO_USERID[steamId] for steamId in steamIds] for (game, steamIds) in steam_games.items()}
    LOG.info("steam games with userId %s", str(steam_games_with_user_id))

    merged_games = {}
    merge_games(merged_games, discord_games)
    merge_games(merged_games, steam_games_with_user_id)
    LOG.info("merged games %s", str(merged_games))
    raw_speech = build_raw_speech(merged_games)

    if len(raw_speech) == 0:
        raw_speech = "No one is playing anything right now."

    LOG.info('raw_speech: ' + raw_speech)
    return speech.build_response({}, speech.build_plain_output_speech(raw_speech))

def get_guild_presences():
    ws = websocket.create_connection(DISCORD_GATEWAY)

    # heartbeat event
    message =  ws.recv()

    ws.send(json.dumps(build_identify()))

    # ready event (don't care)
    ws.recv()

    # guild create event
    message = ws.recv()
    guild_create = json.loads(message)

    ws.close()
    return guild_create['d']['presences']

def build_identify():
    return {
        "op": 2,
        "d": {
            "token": BOT_TOKEN,
            "properties": {
                "$os": "Linux",
                "$browser": "disco",
                "$device": "disco"
            },
            "compress": False
        }
    }

def get_discord_games(presences):
    games = {}
    for presence in presences:
        userId = presence['user']['id']
        game = presence['game']['name']
        if game not in games:
            games[game] = []
        games[game].append(userId)

    return games

def get_steam_player_summaries():
    url = STEAM_PLAYER_SUMMARIES.format(STEAM_API_KEY, ','.join(STEAMID_TO_USERID.keys()))
    LOG.info("steam request: %s", url)
    data = call(url)
    #LOG.info("steam response: %s", json.dumps(data, indent=2))

    return data['response']['players']

def call(url):
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')

    response = urllib.request.urlopen(request)

    return json.loads(response.read())

def get_steam_games(summaries):
    games = {}
    for player in summaries:
        if "gameextrainfo" in player:
            game = player['gameextrainfo']
            steamId = player['steamid']
            if game not in games:
                games[game] = []
            games[game].append(steamId)

    LOG.info("extracted games: %s", str(games))
    return games

def build_raw_speech(games):
    raw_speech = []
    for game, userIds in sorted(games.items(), key=lambda entry: len(entry[1])):
        raw_speech.append(build_game_sentence(game, userIds))
    
    return ' '.join(raw_speech)

def merge_games(merged_games, games):
    for game, userIds in games.items():
        canonicalGame = game.lower()
        if canonicalGame not in merged_games:
            merged_games[canonicalGame] = []

        for userId in userIds:
            if userId not in merged_games[canonicalGame]:
                merged_games[canonicalGame].append(userId)

def build_game_sentence(game, userIds):
    if len(userIds) == 1:
        return USERID_TO_NAME[userIds[0]] + ', is playing ' + game + '.'
    else:
        names = [USERID_TO_NAME[userId] for userId in userIds]
        return ', '.join(names[:-1]) + ', and ' + names[-1] + ', are playing ' + game + '.'
