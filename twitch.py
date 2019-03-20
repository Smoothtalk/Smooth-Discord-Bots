import asyncio
import os
import random
import datetime
import discord

token = ""
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""

discordClient = discord.Client()

@discordClient.event
async def on_message(message):
    upperCase = message.content.upper()
    diceValues = []
    if upperCase.startswith('!D', 0, 2):
        #print (upperCase[2:].strip().get_value())
        try:
            diceNumber = int(upperCase[2:].strip())

            for i in range(0, diceNumber):
                diceValues.append(i)

            diceRoll = random.choice(diceValues)

            await discordClient.send_message(message.channel, diceRoll)
        except:
            await ddiscordClient.send_message(message.channel, "Not a valid dice number")


@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    print('-------')

discordClient.run(token)
