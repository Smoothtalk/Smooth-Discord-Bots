import discord
import asyncio
import random

token = ""

discordClient = discord.Client()

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    print('------')

@discordClient.event
async def on_message(message):
    if message.content.startswith(".c ", 0, 3):
        messageString = message
        choices = message.content[3:].split(',')
        randomChoice = random.choice(choices)

        if (randomChoice.startswith(' ') or randomChoice.endswith(' ')):
            randomChoice = randomChoice.strip(' ')
        #print ('\'' + randomChoice + '\'')

        await discordClient.send_message(message.channel, randomChoice)

discordClient.run(token)
