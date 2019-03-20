import discord
import asyncio
import os
import sys
import random
import datetime
from imgurpython import ImgurClient

token = ''
imgur_client_id = ''
imgur_client_secret = ''
BEAR_IMGUR_ALBUM_ID = ""
H_POST_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""

#bannedUsers = ['', '', '']
bannedUsers = []

imgurClient = ImgurClient(imgur_client_id, imgur_client_secret)
discordClient = discord.Client()

global nextCheck
global checked
global albumURLs
checked = False
currDate = datetime.datetime.today()
nextCheck = currDate + datetime.timedelta(days=1)

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    print('-------')

@discordClient.event
async def on_message(message):
    global nextCheck
    global checked
    global albumURLs

    hPostingChannel = discordClient.get_channel(H_POST_CHANNEL_ID)
    testingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)

    currDate = datetime.datetime.today()
    if(message.author.id in bannedUsers):
        upperCase = ''
    else:
        upperCase = message.content.upper()

    if(checked == False or currDate >= nextCheck):
        print ("getting images")
        albumURLs = imgurClient.get_album_images(BEAR_IMGUR_ALBUM_ID)
        if currDate >= nextCheck:
            nextCheck = currDate + datetime.timedelta(days=1)
        checked = True

    if (upperCase == '!HUPDATE' and message.channel == hPostingChannel):
        print ("getting images manually")
        albumURLs = imgurClient.get_album_images(BEAR_IMGUR_ALBUM_ID)
        nextCheck = currDate + datetime.timedelta(days=1)
        await discordClient.send_message(message.channel, "Manually updated hentai images cache")
        checked = True

    if (upperCase == '!HPOST' and message.channel == hPostingChannel):
        #print (albumURLs[0].id)
        randomURL = random.choice(albumURLs)
        await discordClient.send_message(message.channel, randomURL.link)

    if(upperCase == "!HRESTART" and message.channel == hPostingChannel):
        try:
            await discordClient.send_message(message.channel, "```Restarting hentai bot...```")
            os.execv(__file__)
            await discordClient.send_message(message.channel, "```Restarted hentai bot```")
        except:
            e = sys.exc_info
            print ("This went wrong: " + str(e))
            error_send = "```" + str(e) + "```"
            await discordClient.send_message(message.channel, "```Restarted hentai bot```")

discordClient.run(token)
