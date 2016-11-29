import os
import time
import json
from slackclient import SlackClient
#from flask import Flask

BOT_NAME = 'talking'
BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"
SEND_COMMAND = "send"
START_COMMAND = "start"


#developer_words = ['.net', 'dotnet', 'c#', 'see sharp', 'java', 'php', 'c++', 'python', 'clojure', 'elm', 'haskell', 'F#', 'bash', 'linux', 'ada', 'perl', 'prorgamming', 'objective-c', 'swift', 'ruby', 'JavaScript']

#ux_words = ['UX', 'user experience', 'customer journey', 'customer jurney', 'usability']

general_questions = ['Hi! I am interview bot, why are you the best programmer?'
                     ,'What is your mail address?'
                     ,'What is your name?'
                     ,'What project that you have been a part of was the most fun?'
                     ,'What was your role in that project?'
                     ]

specific_questions = {'.net': 'What about .net?'
                      ,'java': 'What about java?'
                      ,'php': 'What about php?'}

#developer_questions = ['What is the programming language you are best at and what do you like most about it?'
#                       ,'Something'
#                       ,'Do you have any private projects?']

#ux_questions = ['A question about UX'
#                ,'Another question abuot UX'
#                ,'A third one']

question_number = 0

question_types = ""

db =[]
attributes = []

slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    global question_number
    global role
    global question_types

    print question_number
    response = "There might have been some error in my brain processing..."
    if command.startswith(START_COMMAND) or command.startswith('hej') or question_number==0:
        response = general_questions[0]
        question_number += 1
    elif command.startswith(SEND_COMMAND):
        response = "Sending application"
    else:
        for word in specific_questions.keys():
            if word in command:
                attributes.append(word)
        if question_number > len(general_questions):
            question_types = 'specific'
        if question_types == '':
            db.append((general_questions[question_number-1],command))
            print db
            if question_number >= len(general_questions):
                if not attributes:
                    response = "We have no more questions, write send to submit."
                else:
                    e = attributes.pop()
                    response = specific_questions[e]
            else:
                response = general_questions[question_number]
        elif question_types == 'specific':
            if not attributes:
                response = "We have no more questions, write send to submit."
            else:
                e = attributes.pop()
                response = specific_questions[e]

        question_number+=1

    with open('db_sok.json', 'w') as outfile:
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

def parse_slack_output_not_at(slack_rtm_output):
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output:
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
