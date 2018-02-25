import json
import urllib
import speech

from users import USERID_TO_OVERWATCH

PLAYER_NAME_SLOT = "PlayerName"

OWAPI_STATS = "https://owapi.net/api/v3/u/{}/stats"

def handle(request):
    if not request['intent']['name'] == "PlayerRating":
        return speech.build_response({}, "huh?")

    userId = get_user_id(request['intent']['slots'])
    if userId is None:
        if request['dialogState'] == "COMPLETED":
            return speech.build_response({}, "I'm sorry. I don't know who that is.")
        else:
            return speech.build_delegate()

    overwatchRating = get_overwatch_rating(userId)
    print("rating: " + str(overwatchRating))
    #dotaRating = get_dota_rating(userId)

    return speech.build_response({}, overwatchRating)

def get_user_id(slots):
    if 'resolutions' not in slots[PLAYER_NAME_SLOT]:
        return None
    if 'values' not in slots[PLAYER_NAME_SLOT]['resolutions']['resolutionsPerAuthority'][0]:
        return None
    return slots[PLAYER_NAME_SLOT]['resolutions']['resolutionsPerAuthority'][0]['values'][0]['value']['id']

def get_overwatch_rating(userId):
    url = OWAPI_STATS.format(USERID_TO_OVERWATCH[userId])
    request = urllib.request.Request(url)
    request.add_header('User-Agent', 'Mozilla/5.0')

    response = urllib.request.urlopen(request)

    stats = json.loads(response.read())
    return stats['us']['stats']['competitive']['overall_stats']['comprank']