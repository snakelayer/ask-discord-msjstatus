import json
import logging
import speech
import websocket

from users import USERID_TO_NAME


DISCORD_GATEWAY = "wss://gateway.discord.gg/?v=6&encoding=json"
BOT_TOKEN = "<token>"

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def handle(request):
    presences = get_guild_presences()
    presences = [presence for presence in presences if presence['game'] is not None]
    presences = [presence for presence in presences if presence['user']['id'] in USERID_TO_NAME]

    games = get_games(presences)
    LOG.info('games: ' + str(games))

    raw_speech = build_raw_speech(games)

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

def get_games(presences):
    games = {}
    for presence in presences:
        userId = presence['user']['id']
        game = presence['game']['name']
        if game not in games:
            games[game] = []
        games[game].append(userId)

    return games

def build_raw_speech(games):
    raw_speech = []
    for game, userIds in sorted(games.items(), key=lambda entry: len(entry[1])):
        raw_speech.append(build_game_sentence(game, userIds))
    
    return ' '.join(raw_speech)

def build_game_sentence(game, userIds):
    if len(userIds) == 1:
        return USERID_TO_NAME[userIds[0]] + ', is playing ' + game + '.'
    else:
        names = [USERID_TO_NAME[userId] for userId in userIds]
        return ', '.join(names[:-1]) + ', and ' + names[-1] + ', are playing ' + game + '.'
