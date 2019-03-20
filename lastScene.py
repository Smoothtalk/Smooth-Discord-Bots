import discord
import asyncio
import feedparser
import json
import os
import sys
import datetime
import sched, time
from collections import OrderedDict

token = ""
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
DATABASE_LOCATION = "databases/lastOnline.json"

discordClient = discord.Client()

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
        duckServer = discordClient.get_server(DUCKWAD_SERVER_ID)
        duckServerUsers = duckServer.members
        for discord.Member in duckServerUsers:
            # print ("Username: " + discord.Member.name)
            # print ("Status: " + str(discord.Member.status))
            user_dictionary = {'current_status': str(discord.Member.status), 'last_online': 'January 01 1970 00:00 AM EST', 'last_here': 'January 01 1970 00:00 AM EST'} #change this to a datetime later
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

    #return data #an OrderedDict

@discordClient.event
async def on_member_update(memberBefore, memberAfter):
    if (os.stat(DATABASE_LOCATION).st_size != 0): #file not empty
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        if(str(memberBefore.status) == 'online' and str(memberAfter.status) == 'offline'): #going offline
            datetimeFormatted = datetime.datetime.strftime(datetime.datetime.today(), "%B %d %Y %I:%S %p")
            data['Users'][memberBefore.name]['current_status'] = 'offline'
            data['Users'][memberBefore.name]['last_online'] = datetimeFormatted + ' EST'

        if(str(memberBefore.status) == 'offline' and str(memberAfter.status) == 'online'): #coming online
            data['Users'][memberBefore.name]['current_status'] = 'online'

        if(str(memberBefore.status) == 'online' and str(memberAfter.status) == 'idle'): #becoming afk
            datetimeFormatted = datetime.datetime.strftime(datetime.datetime.today(), "%B %d %Y %I:%S %p")
            data['Users'][memberBefore.name]['current_status'] = 'idle'
            data['Users'][memberBefore.name]['last_here'] = datetimeFormatted + ' EST'

        if(str(memberBefore.status) == 'idle' and str(memberAfter.status) == 'online'): #returning from afk
            data['Users'][memberBefore.name]['current_status'] = 'online'

        if(str(memberBefore.status) == 'online' and str(memberAfter.status) == 'dnd'): #becoming afk
            datetimeFormatted = datetime.datetime.strftime(datetime.datetime.today(), "%B %d %Y %I:%S %p")
            data['Users'][memberBefore.name]['current_status'] = 'dnd'
            data['Users'][memberBefore.name]['last_here'] = datetimeFormatted + ' EST'

        if(str(memberBefore.status) == 'dnd' and str(memberAfter.status) == 'online'): #returning from afk
            data['Users'][memberBefore.name]['current_status'] = 'online'

        json_file = open(DATABASE_LOCATION, 'w+')
        json.dump(data, json_file, indent=4)
        json_file.close()

@discordClient.event
async def on_voice_state_update(memberBefore, memberAfter):
    if (os.stat(DATABASE_LOCATION).st_size != 0): #file not empty
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        if(str(not memberBefore.voice.is_afk) and (memberAfter.voice.is_afk)):
            datetimeFormatted = datetime.datetime.strftime(datetime.datetime.today(), "%B %d %Y %I:%M %p")
            data['Users'][memberBefore.name]['current_status'] = 'idle'
            data['Users'][memberBefore.name]['last_here'] = datetimeFormatted + ' EST'

        if(str(memberBefore.voice.is_afk) and (not memberAfter.voice.is_afk)):
            data['Users'][memberBefore.name]['current_status'] = 'online'

        json_file = open(DATABASE_LOCATION, 'w+')
        json.dump(data, json_file, indent=4)
        json_file.close()

@discordClient.event
async def on_message(message):
    if (os.stat(DATABASE_LOCATION).st_size != 0): #file not empty
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        upperCase = message.content.upper()
        cleaner = message.clean_content
        userName = str(cleaner [6:].strip('@'))

        if upperCase.startswith('!SEEN', 0, 5):
            user_Stats = data['Users'].get(userName)
            if(user_Stats is None):
                #no user name or invalid
                await discordClient.send_message(message.channel, "No valid username. (Usernames are case sensitive)")
            else:
                #if(data['Users'][userName]['current_status'] != 'online'): #might break here, change to checking server user's actual status
                duckServer = discordClient.get_server(DUCKWAD_SERVER_ID)
                duckServerUsers = duckServer.members
                for discord.Member in duckServerUsers:
                    if (discord.Member.name == userName and str(discord.Member.status) != 'online'):
                        await discordClient.send_message(message.channel, userName + " was last seen at " + "**" + data['Users'][userName]['last_online'] + "**")
                    elif (discord.Member.name == userName and str(discord.Member.status) == 'online'):
                        await discordClient.send_message(message.channel, "User is already online retard")

        if upperCase.startswith('!HERE', 0, 5):
            user_Stats = data['Users'].get(userName)
            if(user_Stats is None):
                #no user name or invalid
                await discordClient.send_message(message.channel, "No valid username. (Usernames are case sensitive)")
            else:
                #if(data['Users'][userName]['current_status'] != 'online'): #might break here, change to checking server user's actual status
                duckServer = discordClient.get_server(DUCKWAD_SERVER_ID)
                duckServerUsers = duckServer.members
                for discord.Member in duckServerUsers:
                    if (discord.Member.name == userName and str(discord.Member.status) != 'online'):
                        await discordClient.send_message(message.channel, userName + " was last here at " + "**" + data['Users'][userName]['last_here'] + "**")
                    elif (discord.Member.name == userName and str(discord.Member.status) == 'online'):
                        await discordClient.send_message(message.channel, "User is already online retard")

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    database = dataBase_check()
    if(database != False):
        print ("Success")
    elif(database == False):
        print ("Failed Again")
    print('-------')

discordClient.run(token)
