import json
import logging
import intenthandler
import launchhandler
import speech


LOG = logging.getLogger()
LOG.setLevel(logging.INFO)

def handle(event, context):
    LOG.info("Received event: " + json.dumps(event, indent=2))

    speech.speak("Checking.", event['request'], event['context'])

    if event['request']['type'] == "LaunchRequest":
        LOG.info("LaunchRequest")
        return launchhandler.handle(event['request'])
    elif event['request']['type'] == "IntentRequest":
        LOG.info("IntentRequest")
        return intenthandler.handle(event['request'])
    elif event['request']['type'] == "SessionEndedRequest":
        return speech.build_response({}, speech.build_plain_output_speech("Sorry, I misunderstood something."))
