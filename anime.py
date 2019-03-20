import discord
import asyncio
import feedparser
import os
import sys
import datetime
import sched, time
import reconnecting_bot
import aiohttp
import websockets
import logging

HSFEEDURL = ''
UTWFEEDURL = ''
CHINESE_CARTOONS_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
DATABASE_LOCATION = "databases/tidfile"
LOOP_SECONDS = 60
#6 per minute

token = ''

s = sched.scheduler(time.time, time.sleep)
discordClient = discord.Client()

async def HS():
    await discordClient.wait_until_ready()
    chineseCartoonChannel = discordClient.get_channel(CHINESE_CARTOONS_CHANNEL_ID)
    while not discordClient.is_closed:
        try:
            hsFeed = feedparser.parse(HSFEEDURL)
            hsReleases = hsFeed.get('entries') #list of all releases
            releases = []
            for i in hsReleases:
                if len(i) != 1: #DARN 'K' ANIME MESSING EVERYTHING UP, since the title splitter on line 130 picks up only 'k' as the title
                    releases.append(i) #it releases any anime title with 'k' in it

            tidfile = open(DATABASE_LOCATION, 'r+') #stores torrent tids so that they wont download again
            existingTIDs = tidfile.read().split("\n")

            for i in releases:
                #print (i.title)
                title = i.title
                url = i.link
                size = i.nyaa_size
                infoHash = i.nyaa_infohash

                if infoHash not in existingTIDs and 'KiB' not in size:
                    print ("Announcing: " + title)
                    messageToSend = title + " **" + size + "** " + url
                    await discordClient.send_message(chineseCartoonChannel, messageToSend)
                    tidfile.write(infoHash+"\n")

            tidfile.close()
            print ("HS: " + str(len(releases)) + " releases checked")
            print ("Client Disconnected? [HS]:  " + str(discordClient.is_closed))
            await asyncio.sleep(LOOP_SECONDS)
        except:
            e = sys.exc_info()[0]
            print ("This happened [HS]: " + str(e))
            if discordClient.is_closed:
                discordClient._closed.clear()
                discordClient.http.recreate()
            try:
                await discordClient.connect()

            except (discord.HTTPException, aiohttp.ClientError,
                    discord.GatewayNotFound, discord.ConnectionClosed,
                    websockets.InvalidHandshake,
                    websockets.WebSocketProtocolError) as e:
                if isinstance(e, discord.ConnectionClosed) and e.code == 4004:
                    raise # Do not reconnect on authentication failure
                logging.exception("Discord.py [HS] pls keep running")
            await asyncio.sleep(LOOP_SECONDS)

async def UTW():
    await discordClient.wait_until_ready()
    chineseCartoonChannel = discordClient.get_channel(CHINESE_CARTOONS_CHANNEL_ID)
    while not discordClient.is_closed:
        try:
            utwFeed = feedparser.parse(UTWFEEDURL)
            utwReleases = utwFeed.get('entries') #list of all releases
            releases = []
            for i in utwReleases:
                if len(i) != 1: #DARN 'K' ANIME MESSING EVERYTHING UP, since the title splitter on line 130 picks up only 'k' as the title
                    releases.append(i) #it releases any anime title with 'k' in it

            tidfile = open(DATABASE_LOCATION, 'r+') #stores torrent tids so that they wont download again
            existingTIDs = tidfile.read().split("\n")

            for i in releases:
                #special attributes based on RSS feed, unique per rss
                title = i.title
                url = i.link
                size = i.nyaa_size
                infoHash = i.nyaa_infohash

                if infoHash not in existingTIDs and 'KiB' not in size:
                    print ("Announcing: " + title)
                    messageToSend = title + " **" + size + "** " + url
                    await discordClient.send_message(chineseCartoonChannel, messageToSend)
                    tidfile.write(infoHash+"\n")

            tidfile.close()
            print ("UTW: " + str(len(releases)) + " releases checked")
            print ("Client Disconnected? [UTW]: " + str(discordClient.is_closed))
            await asyncio.sleep(LOOP_SECONDS)
        except:
            e = sys.exc_info()[0]
            print ("This happened [UTW]: " + str(e))
            if discordClient.is_closed:
                discordClient._closed.clear()
                discordClient.http.recreate()
            try:
                await discordClient.connect()

            except (discord.HTTPException, aiohttp.ClientError,
                    discord.GatewayNotFound, discord.ConnectionClosed,
                    websockets.InvalidHandshake,
                    websockets.WebSocketProtocolError) as e:
                if isinstance(e, discord.ConnectionClosed) and e.code == 4004:
                    raise # Do not reconnect on authentication failure
                logging.exception("Discord.py [UTW] pls keep running")
            await asyncio.sleep(LOOP_SECONDS)

async def hourly():
    await discordClient.wait_until_ready()

    botTestingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)

    while not discordClient.is_closed:
        #to get your time zone change subtraction from EST
        #timeStamp = datetime.datetime.today().time()
        timeStamp = datetime.datetime.combine(datetime.datetime.today(), datetime.datetime.today().time()) + datetime.timedelta(hours=-2)
        stringTimeStamp = str(timeStamp)
        hour = stringTimeStamp[11:13]
        minute = stringTimeStamp[14:16]
        print ("full time: " + stringTimeStamp)
        print ("hour: " + hour)
        print ("minute: " + minute)

        if(minute == "59" or minute == "00" or minute == "01"):
            datetimeFormatted = datetime.datetime.strftime(timeStamp, "%B %d %Y %I:%M %p")
            await discordClient.send_message(botTestingChannel, "Rocket League sucks at " + datetimeFormatted + " MST")
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
    print('-----')

logger = logging.getLogger('discord')
logger.setLevel(logging.ERROR)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)
discordClient.loop.create_task(HS())
discordClient.loop.create_task(UTW())
asyncio.get_event_loop().run_until_complete(reconnecting_bot.keep_running(discordClient, token))
discordClient.run(token)
