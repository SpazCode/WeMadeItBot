#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import os
import re
import discord
import asyncio
import time
import json
import threading

import httplib2
import requests
import giphypop
from random import randint
from chatterbot import ChatBot
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools

# Discord Client
client = discord.Client()
env = os.environ.get("WemadeitEnv")
pswd = ""
usnm = ""
if env == "production":
    pswd = os.environ.get("password")
    usnm = os.environ.get("username")
else:
    with open("cred.json") as f:
        creds = json.load(f)
        usnm = creds['user']
        pswd = creds['pass']
client.login(usnm, pswd)

# Chatterbot Client
chatbot = ChatBot("BlackWhitby", logic_adapter="chatterbot.adapters.logic.ClosestMatchAdapter")
chatbot.train("chatterbot.corpus.english")
chatbot.train("chatterbot.corpus.english.greetings")
chatbot.train("chatterbot.corpus.english.conversations")
# Todo add corpus for swearing
swearing = {}
with open("corpus/swearing.json") as f:
    swearing = json.load(f)
if "fuck" in swearing.keys():
    for line in swearing["fuck"]:
        chatbot.train(line)
# Drive API
SCOPE = 'https://www.googleapis.com/auth/drive.metadata.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'WeMadeItBot'

# Variables
scores = {}
messageQueue = []
threads = []
threadMax = 4
commands = {
    "!test": "This is a test",
    "!sleep": "Don't turn me off IDK where I go when I sleep",
    "!praise": "+1 to that cool guy (not chris)",
    "!smite": "-1 to that dick guy (chris)",
    "!rankings": "Let's see who the winner is",
    "!absolve": "Wipes the slate clean",
    "!gif": "Sends gif, dud stupid gosh",
    "!dickbutt": "Brings us the glorious dickbutt",
    "!doge": "Such Art, Much Doge, WOW",
    "!no": "NO"
}
sleep_comments = [
    "No No No, please don't never again",
    "...."
]

def get_credentials():
    credential_path = 'wemadeitbot.json'
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

@client.event
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

@client.event
def on_message(message):
    if threading.activeCount() < threadMax:
        t = threading.Thread(target=worker, args=(message, messageQueue))
        t.start()
    else:
        messageQueue.append(message)

def nextMessage(queue):
    lastIndex = len(queue) - 1
    if threading.activeCount() < threadMax and len(queue) > 0:
        message = queue[0]
        del queue[0]
        t = threading.Thread(target=worker, args=(message, queue))
        t.start()

def worker(message, queue):
    print("Starting : " + str(message.id))
    if message.content.startswith('!test'):
        counter = 0
        tmp = client.send_message(message.channel, 'Calculating messages...')
        for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        client.edit_message(tmp, 'You have {} messages.'.format(counter))
    elif message.content.startswith('!sleep'):
        asyncio.sleep(5)
        client.send_message(message.channel, 'Done sleeping')
    elif message.content.startswith('!praise'):
        try:
            to = message.content.split()[1]
        except:
            to = "Not Chris"
        author = message.author
        praise = give_praise(to)
        client.send_message(message.channel, '{0} has praised {1}, they are now @ {2}'.format(author, to, praise))
    elif message.content.startswith('!smite'):
        try:
            to = message.content.split()[1]
        except:
            to = "Chris the Dick"
        author = message.author
        spite = give_spite(to)
        client.send_message(message.channel, '{0} has spited {1}, they are now @ {2}'.format(author, to, spite))
    elif message.content.startswith('!rankings'):
        winner = ['No One', -999999999999999999999]
        for key in scores:
            if scores[key] > winner[1]:
                winner[0] = key
                winner[1] = scores[key]
            client.send_message(message.channel, '{0} has {1} points'.format(key, scores[key]))
        client.send_message(message.channel, '{0} is the winner'.format(winner[0]))
    elif message.content.startswith('!absolve'):
        scores.clear()
        client.send_message(message.channel, 'ALL HAVE BEEN ABSOLVED WE ARE ALL EQUAL NOW')
    elif message.content.startswith('!gif'):
        query = message.content.split()[1:]
        get_gif(message.channel, query)
    elif message.content.startswith('!dickbutt'):
        client.send_message(message.channel, '░░░░░░░░░░░░░░░░░░░░░\n░░░░░░░░░░░░▄▀▀▀▀▄░░░\n░░░░░░░░░░▄▀░░▄░▄░█░░\n░▄▄░░░░░▄▀░░░░▄▄▄▄█░░\n█░░▀▄░▄▀░░░░░░░░░░█░░\n░▀▄░░▀▄░░░░█░░░░░░█░░\n░░░▀▄░░▀░░░█░░░░░░█░░\n░░░▄▀░░░░░░█░░░░▄▀░░░\n░░░▀▄▀▄▄▀░░█▀░▄▀░░░░░\n░░░░░░░░█▀▀█▀▀░░░░░░░\n░░░░░░░░▀▀░▀▀░░░░░░░░')
    elif message.content.startswith('!doge'):
        client.send_message(message.channel, '░░░░░░░░░▄░░░░░░░░░░░░░░▄░░░░\n░░░░░░░░▌▒█░░░░░░░░░░░▄▀▒▌░░░\n░░░░░░░░▌▒▒█░░░░░░░░▄▀▒▒▒▐░░░\n░░░░░░░▐▄▀▒▒▀▀▀▀▄▄▄▀▒▒▒▒▒▐░░░\n░░░░░▄▄▀▒░▒▒▒▒▒▒▒▒▒█▒▒▄█▒▐░░░\n░░░▄▀▒▒▒░░░▒▒▒░░░▒▒▒▀██▀▒▌░░░\n░░▐▒▒▒▄▄▒▒▒▒░░░▒▒▒▒▒▒▒▀▄▒▒▌░░\n░░▌░░▌█▀▒▒▒▒▒▄▀█▄▒▒▒▒▒▒▒█▒▐░░\n░▐░░░▒▒▒▒▒▒▒▒▌██▀▒▒░░░▒▒▒▀▄▌░\n░▌░▒▄██▄▒▒▒▒▒▒▒▒▒░░░░░░▒▒▒▒▌░\n▀▒▀▐▄█▄█▌▄░▀▒▒░░░░░░░░░░▒▒▒▐░\n▐▒▒▐▀▐▀▒░▄▄▒▄▒▒▒▒▒▒░▒░▒░▒▒▒▒▌\n▐▒▒▒▀▀▄▄▒▒▒▄▒▒▒▒▒▒▒▒░▒░▒░▒▒▐░\n░▌▒▒▒▒▒▒▀▀▀▒▒▒▒▒▒░▒░▒░▒░▒▒▒▌░\n░▐▒▒▒▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▒▄▒▒▐░░\n░░▀▄▒▒▒▒▒▒▒▒▒▒▒░▒░▒░▒▄▒▒▒▒▌░░\n░░░░▀▄▒▒▒▒▒▒▒▒▒▒▄▄▄▀▒▒▒▒▄▀░░░\n░░░░░░▀▄▄▄▄▄▄▀▀▀▒▒▒▒▒▄▄▀░░░░░\n░░░░░░░░░▒▒▒▒▒▒▒▒▒▒▀▀░░░░░░░░')
    elif message.content.startswith('!no'):
        client.send_message(message.channel, '▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n▓▓▓▓▓▓▓▓▓───▓▓▓──▓▓▓──────▓▓▓──▓▓▓▓▓\n▓██▓▓▓▓▓▓──▓─▓▓──▓▓──▓▓▓▓──▓▓──▓▓▓▓▓\n▓████▓▓▓▓──▓▓─▓──▓▓──▓▓▓▓──▓▓▓▓▓▓▓▓▓\n▓█▓███▓▓▓──▓▓▓───▓▓▓──────▓▓▓──▓▓▓▓▓\n▓█▓▓███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓\n▓█▓▓▓███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓██▓\n▓█▓▓▓▓███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓███▓\n▓█▓▓▓▓▓███▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓████▓█▓\n▓██████████████████████▓▓▓█████▓▓▓█▓\n▓████░░░░░░░░░░░░░░░░░██████▓▓▓▓▓▓█▓\n███░░░░░░░░░░░░░░░░░░░░░░░██▓▓▓▓▓▓█▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░░██▓▓▓▓██▓\n█░░░░░░░░░█░░░░░░░░░░░░░░░░░██████▓▓\n█░░░████████░░░░█░░░░░░░░░░░░█████▓▓\n█░░█████████░░░░█████░░░░░░░░░███▓▓▓\n█░██▒███████░░░███████████░░░░░██▓▓▓\n█░█▒▒▒███▒██░░░██▒▒█████████░░░█▓▓▓▓\n█░██▒▒▒▒▒▒██░░░█▒▒▒▒████▒▒▒██░░█▓▓▓▓\n█░███▒▒████░░░░█▒▒▒▒███▒▒▒▒▒██░█▓▓▓▓\n█░██████░░░░░░██▒▒▒▒▒▒▒▒▒▒███░░█▓▓▓▓\n█░██░░░░░███░░███▒▒▒▒▒▒▒▒███░░░█▓▓▓▓\n█░░░░░█████░░░░████▒▒▒▒████░░░░█▓▓▓▓\n█░░░░██░░░██░░░███████████░░░░█▓▓▓▓▓\n█░░░██░░░░░██░░░████████░░░░░░█▓▓▓▓▓\n█░░░█░░░░░░░██░░░░███░░░░░░░░█▓▓▓▓▓▓\n█░░░░░░░░░░░░█░░░░░░░░░░░░░░░█▓▓▓▓▓▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░░░█▓▓▓▓▓▓▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░░░█▓▓▓▓▓▓▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░░█▓▓▓▓▓▓▓▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░░█▓▓▓▓▓▓▓▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░█▓▓▓▓▓▓▓▓▓\n█░░░░░░░░░░░░░░░░░░░░░░░░░█▓▓▓▓▓▓▓▓▓\n')
    elif message.content.startswith('!help'):
        for key in commands:
            client.send_message(message.channel, '{0} - {1}'.format(key, commands[key]))
    elif message.content.startswith('!drive'):
        pass
    elif len(message.mentions) == 1:
        user_id = message.mentions[0]
        if str(user_id) == "WeMadeItBot":
            msg = message.content
            msg = re.sub(r'<.*>', '', msg).strip()
            res = chatbot.get_response(str(msg))
            if len(res) > 0:
                client.send_message(message.channel, res)
    print("Ending : " + str(message.id))
    nextMessage(queue)



def send_file(file, channel):
    client.send_file(channel, file)
    os.remove(file)


def get_gif(channel, query):
    g = giphypop.Giphy()
    results = [x for x in g.search(",".join(query))]
    if len(results) > 0:
        num = randint(0, len(results) - 1)
        ts = time.time()
        client.send_message(channel, results[num].media_url)
    else:
        client.send_message(channel, "Couldn't find a gif for you bruh")


def message_log_in(channel):
    client.send_message(channel, 'The Bot has logged in')


def give_praise(person):
    if person in scores.keys():
        scores[person] += 1
    else:
        scores[person] = 1
    return scores[person]


def give_spite(person):
    if person in scores.keys():
        scores[person] -= 1
    else:
        scores[person] = -1
    return scores[person]


def getDriveStatus():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())

client.run()
