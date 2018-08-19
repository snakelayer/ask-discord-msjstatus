import logging
import urllib

DIRECTIVES = '/v1/directives'

LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def build_plain_output_speech(raw_speech):
    return {
        'type': 'PlainText',
        'text': raw_speech
    }

def build_output_speech(raw_speech, type):
    if type == "PlainText":
        return build_output_speech(raw_speech)
    else:
        return {
            'type': 'SSML',
            'ssml': raw_speech
        }

def build_response(session_attributes, output_speech):
    response = {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': {
            'outputSpeech': output_speech,
            'shouldEndSession': True
        }
    }

    if 'text' in output_speech:
        response['response']['card'] = {
                'type': 'Simple',
                'title': "gaming status",
                'content': output_speech['text']
        }
    
    return response;

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
            "requestId": "{}".format(requestId)
        },
        "directive":{
            "type": "VoicePlayer.Speak",
            "speech": "{}".format(message)
        }
    }

    request = urllib.request.Request(url = endpoint + DIRECTIVES, data = urllib.parse.urlencode(directiveData).encode('utf-8'))
    request.add_header('Authorization', 'Bearer ' + accessToken)
    request.add_header('Content-Type', 'application/json')

    try:
        response = urllib.request.urlopen(request)
    except urllib.error.HTTPError as err:
        LOG.error("failed to send speak directive: {} {}".format(err.code, err.reason))
