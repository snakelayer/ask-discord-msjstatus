import logging
import urllib

DIRECTIVES = '/v1/directives'

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def build_response(session_attributes, output_speech):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': output_speech
            },
            'card': {
                'type': 'Simple',
                'title': "msj status",
                'content': output_speech
            },
            'shouldEndSession': True
        }
    }

def build_delegate():
    return {
        'version': '1.0',
        'response': {
            'directives':[  
                {  
                    'type': "Dialog.Delegate"
                }
            ],
            'shouldEndSession': False
        }
    }

def speak(message, request, context):
    endpoint = context['System']['apiEndpoint']
    accessToken = context['System']['apiAccessToken']
    requestId = request['requestId']

    directiveData = {
        "header":{
            "requestId": requestId
        },
        "directive":{
            "type": "VoicePlayer.Speak",
            "speech": message
        }
    }

    request = urllib.request.Request(endpoint + DIRECTIVES, urllib.parse.urlencode(directiveData).encode('utf-8'))
    request.add_header('Authorization', 'Bearer ' + accessToken)
    request.add_header('Content-Type', 'application/json')

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        LOG.error("failed to send speak directive: {} {}".format(err.code, err.reason))