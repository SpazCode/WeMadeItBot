# -*- coding: UTF-8 -*-
import os

import discord
import asyncio
import time
import requests
import giphypop
from random import randint

client = discord.Client()
client.login('blackwhitbywemadeit@outlook.com', '#WeMadeIt')

scores = {}
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


@client.event
def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


@client.event
def on_message(message):
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
        to = message.content.split()[1]
        author = message.author
        praise = give_praise(to)
        client.send_message(message.channel, '{0} has praised {1}, they are now @ {2}'.format(author, to, praise))
    elif message.content.startswith('!smite'):
        to = message.content.split()[1]
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



def send_file(file, channel):
    client.send_file(channel, file)
    os.remove(file)


def get_gif(channel, query):
    g = giphypop.Giphy()
    results = [x for x in g.search(",".join(query))]
    if len(results) > 0:
        num = randint(0, len(results) - 1)
        ts = time.time()
        filepath = "tmp/gif_" + str(int(ts)) + ".gif"
        with open(filepath, 'wb') as f:
            response = requests.get(results[num].media_url, stream=True)
            if not response.ok:
                client.send_message(channel, 'Oh I fucked up try again')
            for block in response.iter_content(1024):
                f.write(block)
            send_file(filepath, channel)
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

client.run()
