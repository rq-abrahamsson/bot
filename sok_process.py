# -*- coding: utf-8 -*-

import os
import sys
import time
import json
from slackclient import SlackClient
#from flask import Flask

reload(sys)
sys.setdefaultencoding('utf-8')

BOT_NAME = 'kim'
BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
SEND_COMMAND = "send"
RESET_COMMAND = "reset"
START_COMMAND = "start"

general_questions = ['Hej! Mitt namn är ' + BOT_NAME + ', jag är Valtechs nya assistent :) Vad kul att du är intresserad av att jobba hos oss! Innan vi kan gå vidare med din ansökan behöver jag veta vad du heter? :)'
                     ,'Hej! Skulle du kunna berätta lite mer om dig själv? Vad driver dig som person?'
                     ,'Cool. Du söker jobbet som systemutvecklare/Lead, kul! Hur trivs du som ledare i en grupp? Ge gärna ett exempel på när du har tagit en ledarroll :)'
                     ,'Låter spännande! Skulle du säga att du trivs bäst med att jobba i grupp eller på egen hand?'
                     ]

specific_questions = {
    '.net': '.Net, grymt! Precis vad vi söker.\nKan du berätta om ett project du är stolt över, där du använt .Net?'
    ,'i grupp': 'Perfekt! På Valtech jobbar vi mycket i grupper, det är därför viktigt att våra medarbetare kan jobba tillsammans. Hur ser din erfarenhet ut inom systemutveckling? Har du några språk eller ramverk du görna jobbar med?'
    ,'på egen hand': 'Vad tråkigt då kan du inte få jobb här!'
    ,'java': 'Java, grymt! Precis vad vi söker.\nKan du berätta om ett project du är stolt över, där du använt Java?'
    ,'php': 'PHP, dåligt! Det vill vi inte ha!'
    ,'javascript': 'JavaScript, grymt! Precis vad vi söker.\nKan du berätta om ett project du är stolt över, där du använt JavaScript? Vad använde du för ramverk.'
    }

question_number = 0
attributes = []
db = []
used_attributes = []
question_types = ""

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def reset():
    global question_number
    global attributes
    global db
    global used_attributes
    global question_types
    question_number = 0
    attributes = []
    db = []
    used_attributes = []
    question_types = ""


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    global question_number
    global role
    global question_types
    response = "There might have been some error in my brain processing..."
    if question_number==0:
        response = general_questions[0]
        question_number += 1
    elif command.startswith("reset"):
        reset()
        response = "Restarted"
    elif command.startswith("help"):
        response = "reset: Restart, send: Send application, help: Show this help text."
    elif command.startswith(SEND_COMMAND):
        response = "Sending application"
    else:
        for word in specific_questions.keys():
            if word in command and not word in used_attributes:
                attributes.append(word)
        if question_number > len(general_questions):
            question_types = 'specific'
        if question_types == '':
            db.append((general_questions[question_number-1],command))
            if question_number >= len(general_questions):
                if not attributes:
                    response = "Vi har inga fler frågor, skriv 'send' för att skicka ansökan."
                else:
                    e = attributes.pop()
                    used_attributes.append(e)
                    response = specific_questions[e]
            else:
                response = general_questions[question_number]
        elif question_types == 'specific':
            if not attributes:
                response = "We have no more questions, write send to submit."
            else:
                e = attributes.pop()
                used_attributes.append(e)
                response = specific_questions[e]

        question_number+=1

    with open('db_sok.json', 'w') as outfile:
        json.dump(db, outfile)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output_not_at(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and output['user'] != BOT_ID:
                # return text after the @ mention, whitespace removed
                return output['text'].lower(), output['channel']
    return None, None

def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print("Bot ID for '" + user['name'] + "' is " + user.get('id'))
                return user.get('id')
    else:
        print("could not find bot user with the name " + BOT_NAME)
        return ''

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    id = get_bot_id()
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        #slack_client.api_call("chat.postMessage", channel='#test',
        #                      text="Hi! Why are you the best programmer?", as_user=True)
        while True:
            message = slack_client.rtm_read()
            command, channel = parse_slack_output_not_at(message)
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
