import asyncio
import os
import random
import datetime
import discord
from discord.ext import commands

token = ""
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
WEDNESDAY_IMAGE_ID = ""
SPOOKY_IMAGE_ID = ""
discordClient = discord.Client()

global wednesdayFound
wednesdayFound = False

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
            await discordClient.send_message(message.channel, "Not a valid dice number")
    if upperCase.startswith('!REGIONAL', 0, 9):
        try:
            await discordClient.edit_message(message, 'FB')
        except Exception as e:
            fmt = 'An error occurred while processing this request: ```py\n{}: {}\n```'
            await discordClient.send_message(message.channel, fmt.format(type(e).__name__, e))


async def isWednesday():
    await discordClient.wait_until_ready()
    global wednesdayFound

    lobbyChannel = discordClient.get_channel(LOBBY_CHANNEL_ID)

    while not discordClient.is_closed:
        isWednesday = False
        isThursday = False

        timeStamp = datetime.datetime.today().time()
        stringTimeStamp = str(timeStamp)
        hour = stringTimeStamp[0:3]
        minute = stringTimeStamp[3:5]
        print ("full time: " + stringTimeStamp)
        print ("hour: " + hour)
        print ("minute: " + minute)

        if(minute == "59" or minute == "00" or minute == "01"):
            # 3=Wednesday 4=Thursday
            todayCode = str(datetime.date.today().strftime("%w"))
            lobbyPins = await discordClient.pins_from(lobbyChannel)

            if(todayCode == "3"):
                isWednesday = True
                isThursday = False
                for message in lobbyPins:
                    if (message.content == WEDNESDAY_IMAGE_ID and wednesdayFound == False):
                        whoMemed = message.author.name
                        alreadyMemedString = whoMemed + " already Wednesday memed today. Good job my dude."
                        await discordClient.send_message(lobbyChannel, alreadyMemedString)
                        wednesdayFound = True

                if (not wednesdayFound):
                    sentMessage = await discordClient.send_message(lobbyChannel, WEDNESDAY_IMAGE_ID)
                    wednesdayFound = True
                    await discordClient.send_message(lobbyChannel, "```Pinning Wednesday```")
                    await discordClient.pin_message(sentMessage)
            elif(todayCode == "4"):
                isThursday = True
                isWednesday = False

                for message in lobbyPins:
                    if (message.content == WEDNESDAY_IMAGE_ID):
                        wednesdayFound = True
                    if (wednesdayFound == True):
                        await discordClient.unpin_message(message)
                        await discordClient.send_message(lobbyChannel, "```Unpinning Wednesday```")
                        wednesdayFound = False

            else:
                isWednesday = False
                isThursday = False
                print ("Not Wednesday or Thursday")

            print ("End of hourly minute loop")
            await asyncio.sleep(3600)
        else:
            minutesLeft = 60 - int(minute)
            print (str(minutesLeft) + " minutes left till next sync")
            secondsLeft = 60 * minutesLeft
            print ("sleeping for " + str(secondsLeft) + " seconds")
            await asyncio.sleep(secondsLeft)


@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    discordClient.loop.create_task(isWednesday())
    print('-------')

discordClient.run(token)
