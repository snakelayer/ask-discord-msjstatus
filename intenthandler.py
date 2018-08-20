import json
import logging
import random
import speech
import urllib

from users import USERID_TO_DOTAID
from users import USERID_TO_OVERWATCHID

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

PLAYER_NAME_SLOT = "PlayerName"

OWAPI_STATS = "https://owapi.net/api/v3/u/{}/stats"
OPENDOTA_PLAYER = "https://api.opendota.com/api/players/{}"

def handle(request):
    if not request['intent']['name'] == "PlayerRating":
        return speech.build_response({}, speech.build_output_speech("huh?"))

    userId = get_user_id(request['intent']['slots'])
    if userId is None:
        if request['dialogState'] == "COMPLETED":
            return speech.build_response({}, speech.build_plain_output_speech("I'm sorry. I don't know who that is."))
        else:
            return speech.build_delegate()

    #overwatchRating = get_overwatch_rating(userId)
    #print("ow: " + str(overwatchRating))
    playerName = get_player_name(request['intent']['slots'])
    if userId not in USERID_TO_DOTAID:
        output_speech = speech.build_plain_output_speech("Does {} really play dota?".format(playerName))
    else:
        dotaRating = get_dota_rating(userId)
        if dotaRating is None:
            output_speech = speech.build_plain_output_speech("{} has no rating. They either need to play more ranked games or make their match data public.".format(playerName))
        else:
            output_speech = speech.build_plain_output_speech("{}'s rating is {}".format(playerName, dotaRating))
            LOG.info("dota: userId=%s, rating=%d", userId, dotaRating)

    if random.randint(0, 9) <= 0:
        output_speech = use_meme_response(output_speech, playerName)
    elif userId == "189977098935468042" and random.randint(0, 2) <= 0:
        output_speech = use_meme_response(output_speech, playerName)
    LOG.info(output_speech)
    return speech.build_response({}, output_speech)

def get_user_id(slots):
    if 'resolutions' not in slots[PLAYER_NAME_SLOT]:
        return None
    if 'values' not in slots[PLAYER_NAME_SLOT]['resolutions']['resolutionsPerAuthority'][0]:
        return None
    return slots[PLAYER_NAME_SLOT]['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']

def get_player_name(slots):
    return slots[PLAYER_NAME_SLOT]['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['name']

def get_overwatch_rating(userId):
    url = OWAPI_STATS.format(USERID_TO_OVERWATCHID[userId])
    data = call(url)

    return data['us']['stats']['competitive']['overall_stats']['comprank']

def get_dota_rating(userId):
    url = OPENDOTA_PLAYER.format(USERID_TO_DOTAID[userId])
    data = call(url)

    if 'mmr_estimate' in data and 'estimate' in data['mmr_estimate']:
        return data['mmr_estimate']['estimate']

    return None

def call(url):
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')

    response = urllib.request.urlopen(request)

    return json.loads(response.read())

def use_meme_response(output_speech, playerName):
    LOG.info("replacing with meme")
    rating = random.randint(500, 1500)
    return speech.build_output_speech("<speak>{}'s rating is {}. <break time=\"1s\"/> <amazon:effect name=\"whispered\"><phoneme alphabet=\"ipa\" ph=\"kɔpa\">kappa</phoneme></amazon:effect>. </speak>".format(playerName, rating), "SSML")
