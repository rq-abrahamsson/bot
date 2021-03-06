import os
import time
import json
from slackclient import SlackClient
#from flask import Flask

BOT_NAME = 'talking'
BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
ADD_COMMAND = "add"

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

class User(object):
    def __init__(self, name, competence, level, _id):
        self.name = name
        self.competence = competence
        self.level = level
        self._id = id

def object_decoder(obj):
    if 'users' in obj:
        array = []
        for user in obj['users']:
            array.append(object_decoder(user))
        return array
    if '__type__' in obj and obj['__type__'] == 'User':
        return User(obj['name'], obj['competence'], obj['level'], obj['_id'])
    return obj

with open('db.json', 'rw') as json_data:
#    db = json.load(json_data, object_hook=object_decoder)
    db = json.load(json_data)
    print(db)
print(db['users'][0])
#app = Flask(__name__)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with numbers, delimited by spaces."
    if command.startswith(EXAMPLE_COMMAND):
        if "add" in command:
            response = "Going to add"
        else:
            response = "Sure...write some more code then I can do that!"
    elif command.startswith(ADD_COMMAND):
        words = command.split()
        if "competence" in command and len(words) > words.index("competence") + 1:
            response = "Adding competence:" + words[words.index("competence")+1]
            db['users'][0]['competence'].append(words[words.index("competence") + 1])
        else:
            response = "Adding something"
    with open('db.json', 'w') as outfile:
        json.dump(db, outfile)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")



#@app.route('/')
#def hello_world():
#    return 'Hello, World!'


#if __name__ == "__main__":
#    api_call = slack_client.api_call("users.list")
#    if api_call.get('ok'):
#        # retrieve all users so we can find our bot
#        users = api_call.get('members')
#        for user in users:
#            if 'name' in user and user.get('name') == BOT_NAME:
#                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
#    else:
#        print("could not find bot user with the name " + BOT_NAME)
