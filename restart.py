import asyncio
import os
import random
import datetime
import discord
import subprocess

token = ""
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
discordClient = discord.Client()

@discordClient.event
async def on_message(message):
    upperCase = message.content.upper()
    if upperCase.startswith('!RESTART', 0, 8) and message.author != discordClient.user:
        try:
            await discordClient.send_message(message.channel, "Restarting " + message.content[9:])
            if(message.content[9:11].upper() == "TTS"):
                await fuckItAll()
        except Exception as e:
            await discordClient.send_message(message.channel, e)


async def fuckItAll():
    command = "pgrep -af python3.5"
    process = subprocess.Popen(['pgrep', '-af', 'python3.5'], stdout=subprocess.PIPE)
    stdout = process.communicate()[0]
    test = str(stdout).split('\\n')
    test[0] = test[0][2:]
    id = -1
    for e in test:
        if("test1.py" in e):
            id = e[:4]
            print (id)

    if(id != -1):
        command = "kill " + id
        process = subprocess.Popen(['kill', id], stdout=subprocess.PIPE)

    os.chdir('/root/python')
    command = "screen -dmS TTS bash -c " + '\'python3.5 ./test1.py\''
    process = subprocess.call(command, shell=True)

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    print('-------')

discordClient.run(token)
