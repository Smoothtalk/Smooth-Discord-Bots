from __future__ import unicode_literals

import discord
import asyncio
import feedparser
import json
import os
import glob
import sys
import datetime
import sched, time
import youtube_dl
from gtts import gTTS
from collections import OrderedDict
from pydub import AudioSegment

token = ''
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
LOBBY_VOICE_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
MUSIC_REQUESTS_CHANNEL_ID = ""
DATABASE_LOCATION = "databases/TTS.json"
DEFAULT_TTS = "Rocket League Sucks"
TTS_JOIN_FILES_LOCATION = "/root/python/tts/join/"
TTS_LEAVE_FILES_LOCATION = "/root/python/tts/leave/"
TTS_JOIN_LOBBY_MP3_FILE = "Joined Lobby.mp3"
TTS_LEAVE_LOBBY_MP3_FILE = "Leave Lobby.mp3"
discordClient = discord.Client()

global state

class VoiceState:
    def __init__(self, discordClient):
        self.voice = None
        self.discordClient = discordClient
        self.is_done = False

    async def play_tts(self, player):
        player.start()

        while(player.is_playing()):
            self.is_done = False

        if(player.is_playing() == False):
            self.is_done = True

def dataBase_check():
    global state
    state = VoiceState(discordClient)
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
            if(not discord.Member.bot):
                user_dictionary = {'TTS': DEFAULT_TTS} #change this to a datetime later
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

@discordClient.event
async def on_message(message):
    upperCase = message.content.upper()
    if(upperCase.startswith('!TTS', 0, 4) and message.channel.is_private):

        os.chdir("/root/python/tts")
        joinMp3 = AudioSegment.from_mp3(TTS_JOIN_LOBBY_MP3_FILE)
        leaveMp3 = AudioSegment.from_mp3(TTS_LEAVE_LOBBY_MP3_FILE)
        os.chdir("/root/python")

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
                }],
        }

        ttsContent = str(message.content[4:].strip()) #building content
        print (ttsContent)
        await discordClient.send_message(message.author, "url recived")

        os.chdir("/root/python/youtubeMp3s")

        await discordClient.send_message(message.author, "Downloading...")

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([ttsContent])
            info_dict = ydl.extract_info(ttsContent, download=False)
            video_url = info_dict.get("url", None)
            video_id = info_dict.get("id", None)
            video_title = info_dict.get('title', None)

        fileName = "*-" + video_id + ".mp3"
        for file in glob.glob(fileName):
            print ("It's there")
            fullYTMp3 = AudioSegment.from_mp3(file)

            #can put a def check here
            await discordClient.send_message(message.author, "Enter a start time in the format of XX:XX")
            start_time_Message = await discordClient.wait_for_message(author=message.author)

            await discordClient.send_message(message.author, "Enter an end time in the format of XX:XX")
            end_time_Message = await discordClient.wait_for_message(author=message.author)

            minutesStartTime = int(start_time_Message.content.replace(':', '')) // 60
            secondsStartTime = int(start_time_Message.content.replace(':', '')) % 60
            startTime = ((minutesStartTime * 60) + secondsStartTime) * 1000

            minutesEndTime = int(end_time_Message.content.replace(':', '')) // 60
            secondsEndTime = int(end_time_Message.content.replace(':', '')) % 60
            endTime = ((minutesEndTime * 60) + secondsEndTime) * 1000

            newSegment = fullYTMp3[startTime:endTime]

            newJoinMp3 = newSegment + joinMp3
            newLeaveMp3 = newSegment + leaveMp3

            os.chdir("/root/python/tts/join")
            newJoinMp3.export(message.author.name + ".mp3", format="mp3")
            os.chdir("/root/python/tts/leave")
            newLeaveMp3.export(message.author.name + ".mp3", format="mp3")

            await discordClient.send_message(message.author, "Successfully changed")

        os.chdir("/root/python")

    if(upperCase.startswith("!TTS REDUCE", 0, 11) and message.channel.is_private):
        filename = message.author.name + ".mp3"

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python")

        await discordClient.send_message(message.author, "Type the amount of db to reduce TTS by")
        reduceByMessage = await discordClient.wait_for_message(author=message.author)

        reduceAmount = int(reduceByMessage.content)

        joinTTSNew = joinTTS - reduceAmount
        leaveTTSNew = leaveTTS - reduceAmount

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTSNew.export(message.author.name + ".mp3", format="mp3")

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTSNew.export(message.author.name + ".mp3", format="mp3")

        await discordClient.send_message(message.author, "Success decreased")

    if(upperCase.startswith("!TTS INCREASE", 0, 13) and message.channel.is_private):
        filename = message.author.name + ".mp3"

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python")

        await discordClient.send_message(message.author, "Type the amount of db to increase TTS by")
        increaseByMessage = await discordClient.wait_for_message(author=message.author)

        increaseAmount = int(increaseByMessage.content)

        joinTTSNew = joinTTS - increaseAmount
        leaveTTSNew = leaveTTS - increaseAmount

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTSNew.export(message.author.name + ".mp3", format="mp3")

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTSNew.export(message.author.name + ".mp3", format="mp3")

        await discordClient.send_message(message.author, "Successfully increased")

@discordClient.event
async def on_voice_state_update(memberBefore, memberAfter):
    await discordClient.wait_until_ready()
    global state

    os.chdir("/root/python")
    if (os.stat(DATABASE_LOCATION).st_size != 0): #file not empty
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        lobbyVoiceChannel = discordClient.get_channel(LOBBY_VOICE_CHANNEL_ID)
        botTestingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)
        if(memberBefore.voice.voice_channel != lobbyVoiceChannel and memberAfter.voice.voice_channel == lobbyVoiceChannel):
            if(memberAfter.name in data['Users']):
                #tts = gTTS(text=data['Users'][memberBefore.name]['TTS']  + " has connected", lang='en', slow=False)
                tts = gTTS(text=data['Users'][memberAfter.name]['TTS']  + " has joined lobby", lang='en', slow=False)
                fileName = TTS_JOIN_FILES_LOCATION + memberAfter.name + '.mp3'
                if(not os.path.isfile(fileName)):
                    print ("File Create: " + fileName)
                    tts.save(fileName)
                try:
                    if state.voice is None:
                        print ("1")
                        print ("before: " + type(state.voice))
                        state.voice = await discordClient.join_voice_channel(lobbyVoiceChannel)
                        print ("after:" + type(state.voice))
                        print ("2")
                    else:
                        print ("3")
                        await state.voice.move_to(lobbyVoiceChannel)
                        print("4")
                    try:
                        opts = {
                            'quiet': True,
                        }
                        player = state.voice.create_ffmpeg_player(fileName, options=opts)
                    except Exception as e:
                        fmt = 'An inner error occurred while processing this request: ```py\n{}: {}\n```'
                        await discordClient.send_message(message.channel, fmt.format(type(e).__name__, e))
                    else:
                        player.volume = 0.5
                        await state.play_tts(player)

                except:
                    e = sys.exc_info()[0]
                    print ("This happened [TTS1]: " + str(e))
                    if discordClient.is_closed:
                        discordClient._closed.clear()
                        discordClient.http.recreate()
                    try:
                        await discordClient.connect()
                        state.voice = None
                        state.is_done = None

                    except (discord.HTTPException, aiohttp.ClientError,
                            discord.GatewayNotFound, discord.ConnectionClosed,
                            websockets.InvalidHandshake,
                            websockets.WebSocketProtocolError) as e:
                        if isinstance(e, discord.ConnectionClosed) and e.code == 1001:
                            raise # Do not reconnect on authentication failure
                        logging.exception("Discord.py [TTS2] pls keep running")

        if(memberBefore.voice.voice_channel == lobbyVoiceChannel and memberAfter.voice.voice_channel != lobbyVoiceChannel):
            if ((state.voice is not None) and (len(lobbyVoiceChannel.voice_members) == 1 and (discordClient.user in lobbyVoiceChannel.voice_members))):
                print ("5")
                await state.voice.disconnect()
                state.voice = None
                state.is_done = None

            elif(memberBefore.name in data['Users']):
                #tts = gTTS(text=data['Users'][memberBefore.name]['TTS']  + " has connected", lang='en', slow=False)
                fileName = TTS_LEAVE_FILES_LOCATION + memberBefore.name + '.mp3'

                try:
                    if state.voice is None:
                        state.voice = await discordClient.join_voice_channel(lobbyVoiceChannel)
                    else:
                        await state.voice.move_to(lobbyVoiceChannel)

                    try:
                        opts = {
                            'quiet': True,
                        }
                        player = state.voice.create_ffmpeg_player(fileName, options=opts)
                    except Exception as e:
                        fmt = 'An inner error occurred while processing this request: ```py\n{}: {}\n```'
                        await discordClient.send_message(message.channel, fmt.format(type(e).__name__, e))
                    else:
                        player.volume = 0.5
                        state.is_done = True
                        await state.play_tts(player)
                except:
                    e = sys.exc_info()[0]
                    print ("This happened [TTS2]: " + str(e))
                    if discordClient.is_closed:
                        discordClient._closed.clear()
                        discordClient.http.recreate()
                    try:
                        await discordClient.connect()
                        state.voice = None
                        state.is_done = None

                    except (discord.HTTPException, aiohttp.ClientError,
                            discord.GatewayNotFound, discord.ConnectionClosed,
                            websockets.InvalidHandshake,
                            websockets.WebSocketProtocolError) as e:
                        if isinstance(e, discord.ConnectionClosed) and e.code == 1001:
                            raise # Do not reconnect on authentication failure
                        logging.exception("Discord.py [TTS3] pls keep running")

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    database = dataBase_check()
    print('-------')

discordClient.run(token)
