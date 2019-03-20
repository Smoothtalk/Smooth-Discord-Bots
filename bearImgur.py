import discord
import asyncio
import os
import random
import datetime
from imgurpython import ImgurClient

token = ''
imgur_client_id = ''
imgur_client_secret = ''
BEAR_IMGUR_ALBUM_ID = ""
H_POST_CHANNEL_ID = "
BOTTESTING_CHANNEL_ID = ""

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

    currDate = datetime.datetime.today()

    hPostingChannel = discordClient.get_channel(H_POST_CHANNEL_ID)
    testingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)
    upperCase = message.content.upper()

    if(checked == False or currDate >= nextCheck):
        print ("getting images")
        albumURLs = imgurClient.get_album_images(BEAR_IMGUR_ALBUM_ID)
        if currDate >= nextCheck:
            nextCheck = currDate + datetime.timedelta(days=1)
        checked = True

    if (upperCase == ('!RUPDATE') and message.channel == hPostingChannel):
        albumURLs = imgurClient.get_album_images(BEAR_IMGUR_ALBUM_ID)
        nextCheck = currDate + datetime.timedelta(days=1)
        await discordClient.send_message(message.channel, "Manually updated random images cache")
        checked = True

    if (upperCase == ('!RANDOM') and message.channel == hPostingChannel):
        #print (albumURLs[0].id)
        randomURL = random.choice(albumURLs)
        await discordClient.send_message(message.channel, randomURL.link)

discordClient.run(token)
