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
from gtts import gTTS
from collections import OrderedDict
from pydub import AudioSegment
from threading import Thread
from time import sleep

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

class TTSEntry:
    def __init__(self, player):
        self.player = player

class VoiceState:
    def __init__(self, discordClient):
        self.current = None
        self.voice = None
        self.discordClient = discordClient
        self.play_next = asyncio.Event()
        self.TTSS = asyncio.Queue()
        self.audio_player = self.discordClient.loop.create_task(self.play_tts())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def toggle_next(self):
        self.discordClient.loop.call_soon_threadsafe(self.play_next.set)

    async def play_tts(self):
        while True:
            self.play_next.clear()
            self.current = await self.TTSS.get()
            self.current.player.start()
            await self.play_next.wait()

class TTS:
    """Voice related commands.
    Works in multiple servers at once.
    """
    def __init__(self, discordClient):
        self.discordClient = discordClient
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.discordClient)
            self.voice_states[server.id] = state
        return state

    async def create_voice_client(self, channel):
        voice = await self.discordClient.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.discordClient.loop.create_task(state.voice.disconnect())
            except:
                pass

    async def join(self, channel : discord.Channel):
        """Joins a voice channel."""
        botTestingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)
        try:
            return await self.create_voice_client(channel)
        except discord.ClientException:
            pass
        except discord.InvalidArgument:
            await discordClient.send_message(botTestingChannel, 'This is not a voice channel...')

    async def play(self, server, fileName : str):
        state = self.get_voice_state(server)

        opts = {
            'quiet': True,
        }

        if state.voice is None:
            success = await self.join(server.voice_client.channel)
            if not success:
                return

        try:
            opts = {
            'quiet': True,
            }
            player = state.voice.create_ffmpeg_player(fileName, options=opts, after=state.toggle_next)
            player.volume = 0.5
        except Exception as e:
            botTestingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)
            fmt = 'An inner error occurred while processing this request: ```py\n{}: {}\n```'
            await discordClient.send_message(botTestingChannel, fmt.format(type(e).__name__, e))
        else:
            entry = TTSEntry(player)
            await state.TTSS.put(entry)

    async def disconnect(self, server):
        """Stops playing audio and leaves the voice channel.
        This also clears the queue.
        """
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
        except:
            pass

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

async def youtube_download(url, user):
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

    ttsContent = str(url[4:].strip()) #building content
    print (ttsContent)
    await discordClient.send_message(user, "url recived")

    os.chdir("/root/python/youtubeMp3s")

    await discordClient.send_message(user, "Downloading...")

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
        await discordClient.send_message(user, "Enter a start time in the format of XX:XX")
        start_time_Message = await discordClient.wait_for_message(author=user)

        await discordClient.send_message(user, "Enter an end time in the format of XX:XX")
        end_time_Message = await discordClient.wait_for_message(author=user)

        minutesStartTime = int(start_time_Message.content.split(':')[0])
        secondsStartTime = int(start_time_Message.content.split(':')[1])
        startTimeMS = ((minutesStartTime * 60) + secondsStartTime) * 1000

        minutesEndTime = int(end_time_Message.content.split(':')[0])
        secondsEndTime = int(end_time_Message.content.split(':')[1])
        endTimeMS = ((minutesEndTime * 60) + secondsEndTime) * 1000

        newSegment = fullYTMp3[startTimeMS:endTimeMS]

        newJoinMp3 = newSegment + joinMp3
        newLeaveMp3 = newSegment + leaveMp3

        os.chdir("/root/python/tts/join")
        newJoinMp3.export(user.name + ".mp3", format="mp3")
        os.chdir("/root/python/tts/leave")
        newLeaveMp3.export(user.name + ".mp3", format="mp3")

        await discordClient.send_message(user, "Successfully changed")

    os.chdir("/root/python")

@discordClient.event
async def on_message(message):
    upperCase = message.content.upper()

    if(upperCase == "!TTS REDUCE" and message.channel.is_private):
        fileName = message.author.name + ".mp3"

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

    elif(upperCase == "!TTS INCREASE" and message.channel.is_private):
        fileName = message.author.name + ".mp3"

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

    elif(upperCase.startswith('!TTS', 0, 4) and message.channel.is_private):
        discordClient.loop.create_task(youtube_download(message.content, message.author))

@discordClient.event
async def on_voice_state_update(memberBefore, memberAfter):
    await discordClient.wait_until_ready()
    global announceTTS
    global state

    os.chdir("/root/python")
    if (os.stat(DATABASE_LOCATION).st_size != 0): #file not empty
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        lobbyVoiceChannel = discordClient.get_channel(LOBBY_VOICE_CHANNEL_ID)
        botTestingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)

        if(memberBefore.voice.voice_channel != lobbyVoiceChannel and memberAfter.voice.voice_channel == lobbyVoiceChannel and memberBefore.top_role.name != "%bot"):
            state = announceTTS.get_voice_state(memberAfter.server)

            if(memberAfter.name in data['Users']):
                fileName = TTS_JOIN_FILES_LOCATION + memberAfter.name + '.mp3'

                if(not os.path.isfile(fileName)):
                    print ("Error " + fileName + "does not exist")

                try:
                    if(state.voice is None):
                        await announceTTS.join(lobbyVoiceChannel)
                        print("Connected to: " + announceTTS.voice_states[DUCKWAD_SERVER_ID].voice.channel.name)
                    await announceTTS.play(memberAfter.server, fileName)
                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [TTS1]: " + str(e))

        if(memberBefore.voice.voice_channel == lobbyVoiceChannel and memberAfter.voice.voice_channel != lobbyVoiceChannel):
            state = announceTTS.get_voice_state(memberAfter.server)

            if ((state is not None) and (len(lobbyVoiceChannel.voice_members) == 1 and (discordClient.user in lobbyVoiceChannel.voice_members))):
                await announceTTS.disconnect(memberAfter.server)

            elif(memberBefore.name in data['Users'] and memberBefore.top_role.name != "%bot"):
                fileName = TTS_LEAVE_FILES_LOCATION + memberBefore.name + '.mp3'
                try:
                    #await announceTTS.summon(memberAfter)
                    if(state.voice is None):
                        await announceTTS.join(lobbyVoiceChannel)
                        print("Connected to: " + announceTTS.voice_states[DUCKWAD_SERVER_ID].voice.channel.name)
                    await announceTTS.play(memberAfter.server, fileName)

                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [TTS2]: " + str(e))

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    database = dataBase_check()
    global state
    global announceTTS
    state = VoiceState(discordClient)
    announceTTS = TTS(discordClient)
    print('-------')

discordClient.run(token)
