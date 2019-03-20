from __future__ import unicode_literals

import discord
import asyncio
import feedparser
import json
import os
import glob
import sys
import datetime
import aiohttp
import websockets
import sched, time
import youtube_dl
import traceback
import random
from gtts import gTTS
from collections import OrderedDict
from pydub import AudioSegment
from threading import Thread
from multiprocessing.pool import ThreadPool
from time import sleep
from imgurpython import ImgurClient
from discord.ext import commands

token = ""
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
PREMIUM_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
LOOTBOX_CHANNEL_ID = ""
DATABASE_LOCATION = "databases/lootbot.json"
imgur_client_id = ''
imgur_client_secret = '17f03c3c19575201e49524729aee0a3f01b487a6'
WAIFU_IMGUR_ALBUM_ID = ""
MEME_IMGUR_ALBUM_ID = ""

imgurClient = ImgurClient(imgur_client_id, imgur_client_secret)
bot = discord.Client()

global albumURLs

MIN_RNG_VALUE = 1
MAX_RNG_VALUE = 99
LOOTBOX_COST = 40

class LootBox:
    def __init__(self, message, bot):
        self.chain = False
        self.cost = LOOTBOX_COST
        self.bot = bot
        self.rolled = 0
        self.Hidden_Variables = False
        self.channel = message.channel
        self.whoSpent = message.author.name
        self.author = message.author
        self.lootboxChannel = self.bot.get_channel(LOOTBOX_CHANNEL_ID)

    async def prize_Select(self, rolledNumber):
        self.rolled = rolledNumber
        #await bot.send_message(self.channel, "You rolled a **" + str(rolledNumber) + "**")

        if(0 < rolledNumber <= 1):
            await self.waifuRoll()
        elif(2 <= rolledNumber <= 6):
            await self.premiumMemberShipRoll(self.whoSpent)
            await bot.send_message(self.lootboxChannel, "CONGRATS ON WINNING PREMIUM " + self.whoSpent)
            await bot.send_message(self.lootboxChannel, "You should be able to talk for a day on the Premium Channel")
            await bot.send_message(self.lootboxChannel, "Please wait 2 minutes while we change your permissions")
        elif(7 <= rolledNumber <= 11):
            await self.memeRoll()
        elif(12 <= rolledNumber <= 20):
            self.chain = True
            await bot.send_message(self.lootboxChannel, self.whoSpent + " got another lootbox")
            self.addToTotal(self.whoSpent)
            theRoll = random.randint(MIN_RNG_VALUE, MAX_RNG_VALUE)
            await self.prize_Select(theRoll)
        elif(21 <= rolledNumber <= 30):
            await self.complimentRoll()
        elif(31 <= rolledNumber <= 99):
            await self.anotherRandomNumberRoll()
        else:
            await bot.send_message(self.lootboxChannel, "Something Fucked up. Blame Smooth")

    async def waifuRoll(self):
        albumURLs = imgurClient.get_album_images(WAIFU_IMGUR_ALBUM_ID)
        randomURL = random.choice(albumURLs)
        await bot.send_message(self.lootboxChannel, "WAIFU 4 " + self.whoSpent)
        await bot.send_message(self.lootboxChannel, randomURL.link)

    async def premiumMemberShipRoll(self, whoSpent):
        datetimeFormatted = datetime.datetime.strftime(datetime.datetime.today() + datetime.timedelta(days=1), "%B %d %Y %I:%S %p")

        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        data['Users'][whoSpent]['Premium'] = True
        data['Users'][whoSpent]['Expiration'] = datetimeFormatted + ' EST'

        json_file = open(DATABASE_LOCATION, 'w+')
        json.dump(data, json_file, indent=4)
        json_file.close()

    async def memeRoll(self):
        albumURLs = imgurClient.get_album_images(MEME_IMGUR_ALBUM_ID)
        randomURL = random.choice(albumURLs)
        await bot.send_message(self.lootboxChannel, "MEME 4 " + self.whoSpent)
        await bot.send_message(self.lootboxChannel, randomURL.link)
        # await bot.send_message(self.channel, "Duckwad is slow to respond so I don't have a meme imgur album")

    async def complimentRoll(self):
        messageToSend = "Random Compliment for " + self.whoSpent + " : " + "I'm sure Hitler loves you"
        await bot.send_message(self.lootboxChannel, messageToSend)

    async def anotherRandomNumberRoll(self):
        x = random.randint(1, 99)
        messageToSend = "Here's your random number " + self.whoSpent + " : **" + str(x) + '**'
        await bot.send_message(self.lootboxChannel, messageToSend)
        await bot.send_message(self.lootboxChannel, "Thanks for Playing")

    def addToTotal(self, whoSpent): #add money spent to json value and write to file
        try:
            print ("Adding to total")
            json_data = open(DATABASE_LOCATION).read()
            data = json.loads(json_data, object_pairs_hook=OrderedDict)

            data['Users'][whoSpent]['Money Spent'] = data['Users'][whoSpent]['Money Spent'] + LOOTBOX_COST #TODO maybe need an explict int convert here

            json_file = open(DATABASE_LOCATION, 'w+')
            json.dump(data, json_file, indent=4)
            json_file.close()
        except:
            e = sys.exc_info()[0]
            print ("Exception @ " + str(e))

def dataBase_check():
    try:
        print ("trying")
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)
        return data
    except:
        e = sys.exc_info()[0]
        print ("Exception @ " + str(e))
        #get Users
        users = {'Users': {}}
        duckServer = bot.get_server(DUCKWAD_SERVER_ID)
        duckServerUsers = duckServer.members
        for discord.Member in duckServerUsers:
            # print ("Username: " + discord.Member.name)
            # print ("Status: " + str(discord.Member.status))
            if(not discord.Member.bot):
                user_dictionary = {'Money Spent': 0, 'Premium': False,  'Expiration': 'January 01 1970 00:00 AM EST'} #change this to a datetime later?
                users['Users'][discord.Member.name] = user_dictionary

        json_file = open(DATABASE_LOCATION, 'w+')
        json.dump(users, json_file, indent=4)
        json_file.close()

        try:
            print ("trying2")
            json_data = open(DATABASE_LOCATION).read()
            data = json.loads(json_data, object_pairs_hook=OrderedDict)
            return data
        except:
            e = sys.exc_info()[0]
            print ("Exception 2@ " + str(e))
            return False

async def updatePremium():
    await bot.wait_until_ready()

    while not bot.is_closed:
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        premiumChannel = bot.get_channel(PREMIUM_CHANNEL_ID)
        duckServer = list(bot.servers)[0]
        overwrite = discord.PermissionOverwrite()

        for user, userValues in data['Users'].items():
            if (userValues['Premium'] != False):
                today = datetime.datetime.strftime(datetime.datetime.today(), "%B %d %Y %I:%S %p") #January 01 1970 00:00 AM EST
                datetimeFormattedToday = datetime.datetime.strptime(today, "%B %d %Y %I:%S %p")

                expiration = userValues['Expiration']
                noZoneExpiration = expiration[:-4]
                datetimeFormattedExpiration = datetime.datetime.strptime(noZoneExpiration, "%B %d %Y %I:%S %p")

                if(datetimeFormattedExpiration < datetimeFormattedToday): #will probably error here
                    #change channel permissions to remove premium
                    userValues['Premium'] = False
                    overwrite.send_messages = False
                else:
                    #change channel permissions to give premium
                    overwrite.send_messages = True

                try:
                    await bot.edit_channel_permissions(premiumChannel, duckServer.get_member_named(user), overwrite)
                except:
                    e = sys.exc_info()[0]
                    print ("Exception 3@ " + str(e))

        json_file = open(DATABASE_LOCATION, 'w+')
        json.dump(data, json_file, indent=4)
        json_file.close()

        await asyncio.sleep(60)

def getTotalOf(whoSpent): #get the Money Spent of a user
    try:
        print ("Getting total")
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        return data['Users'][whoSpent]['Money Spent']
        json_file.close()
    except:
        e = sys.exc_info()[0]
        print ("Exception @ " + str(e))

@bot.event
async def on_message(message):
    upperCase = message.content.upper()
    lbChannel = bot.get_channel(LOOTBOX_CHANNEL_ID)
    if (message.channel == lbChannel):
        if(upperCase == "!BUYLOOTBOX"):
            if(message.author.id != ""):
                if(message.author.id == ""):
                    await bot.send_message(message.channel, "Just try and break my bot (you probably will)")
                elif(message.author.id == ""):
                    await bot.send_message(message.channel, "Hi Ben")
                newLootBox = LootBox(message, bot)
                if(message.author.id == ""):
                    theRoll = random.randint(1, 1)
                elif(message.author.id == ""):
                    theRoll = random.randint(1, 30)
                else:
                    theRoll = random.randint(MIN_RNG_VALUE, MAX_RNG_VALUE)
                await newLootBox.prize_Select(theRoll)
                newLootBox.addToTotal(message.author.name)
            else:
                await bot.send_message(message.channel, "Sorry you've sucked too much dick to roll lootboxes")
        elif(upperCase == "!SPENT"):
            amount = getTotalOf(message.author.name)
            messageToSend = message.author.name + " has spent $" + str(amount) + " Canadian Dollars on lootboxes. Way to go"
            await bot.send_message(message.channel, messageToSend)
        elif(upperCase == "!PREMIUM"):
            json_data = open(DATABASE_LOCATION).read()
            data = json.loads(json_data, object_pairs_hook=OrderedDict)

            expirationDate = data['Users'][message.author.name]['Expiration']
            messageToSend = message.author.name + "\'s premium expires at: " + str(expirationDate)

            await bot.send_message(message.channel, messageToSend)
            #return the expiration date of their premium

@bot.event
async def on_ready():
    database = dataBase_check()
    bot.loop.create_task(updatePremium())
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

bot.run(token)
