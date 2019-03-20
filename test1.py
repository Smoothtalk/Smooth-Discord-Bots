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
from random import *
from gtts import gTTS
from collections import OrderedDict
from pydub import AudioSegment
from threading import Thread
from multiprocessing.pool import ThreadPool
from time import sleep
from discord.ext import commands

token = ''

#needy ben, clingy ona
bannedUsers = ['', '']

DUCKWAD_SERVER_ID = ""

LOBBY_VOICE_CHANNEL_ID = ""
THE_GAME_VOICE_CHANNEL_ID = ""
ANOTHER_GAME_VOICE_CHANNEL_ID = ""
ANTI_BEN_VOICE_CHANNEL_ID = ""
BOTTESTING_VOICE_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = "" #for error reporting
MUSIC_REQUESTS_CHANNEL_ID = ""

DATABASE_LOCATION = "databases/TTS.json"
DEFAULT_TTS = "Rocket League Sucks"

TTS_JOIN_FILES_LOCATION = "/root/python/tts/join/"
TTS_LEAVE_FILES_LOCATION = "/root/python/tts/leave/"
TTS_JOIN_LOBBY_MP3_FILE = "Joined Lobby.mp3"
TTS_LEAVE_LOBBY_MP3_FILE = "Leave Lobby.mp3"

EMPTY = 'Empty'
bot = discord.Client()

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')

class VoiceEntry:
    def __init__(self, player):
        self.player = player

class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())
        self.bot.loop.create_task(self.websocket_check())

    async def websocket_check(self):
        if (self.voice is not None):
            self.voice.poll_voice_ws()
        await asyncio.sleep(1)

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            print("Audio Playing Task")
            self.play_next_song.clear()
            print("Clearing Next Song")
            self.current = await self.songs.get()
            print("Getting \"Current\"")
            self.current.player.start()
            print("Start playing")
            await self.play_next_song.wait()
            print("Wait for next song")

class Music:
    """Voice related commands.

    Works in multiple servers at once.
    """
    def __init__(self, bot):
        self.bot = bot
        self.loop = bot.loop
        self.voice_states = {}
        self.voice_client_connect_lock = asyncio.Lock()

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        with await self.voice_client_connect_lock:
            voice = await self.bot.join_voice_channel(channel)
            state = self.get_voice_state(channel.server)
            state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    async def join(self, channel : discord.Channel):
        """Joins a voice channel."""
        try:
            await self.create_voice_client(channel)
        except discord.ClientException:
            pass
        except discord.InvalidArgument:
            print ("Invalid Arg")

    async def play(self, member, song : str):
        """Plays a song.

        If there is a song currently in the queue, then it is
        queued until the next song is done playing.

        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(member.server)
        print ("Playing to: " + member.voice.voice_channel.name)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.join(member.voice.voice_channel))
            if not success:
                return

        try:
            player = state.voice.create_ffmpeg_player(song, options=opts, after=state.toggle_next)
        except Exception as e:
            botTestingChannel = bot.get_channel(BOTTESTING_CHANNEL_ID)
            fmt = 'An inner error occurred while processing this request: ```py\n{}: {}\n```'
            await bot.send_message(botTestingChannel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(player)
            print ('Creating Entry')
            await state.songs.put(entry)
            print ('Adding \'Entry\' to queue')

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
        duckServer = bot.get_server(DUCKWAD_SERVER_ID)
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
    try:
        os.chdir("/root/python/tts")
        joinMp3 = AudioSegment.from_mp3(TTS_JOIN_LOBBY_MP3_FILE)
        leaveMp3 = AudioSegment.from_mp3(TTS_LEAVE_LOBBY_MP3_FILE)
        os.chdir("/root/python")

        ttsContent = str(url[4:].strip()) #building content
        print (ttsContent)
        await bot.send_message(user, "url recived")

        await bot.send_message(user, "Downloading...")

        pool = ThreadPool(processes=1)
        async_result = pool.apply_async(youTubeVideoDownload, (ttsContent,))
        # downloadThread = Thread(target = youTubeVideoDownload, args = (ttsContent))
        # downloadThread.start()

        #can put a def check here
        await bot.send_message(user, "Enter a start time in the format of XX:XX")
        start_time_Message = await bot.wait_for_message(author=user)

        await bot.send_message(user, "Enter an end time in the format of XX:XX")
        end_time_Message = await bot.wait_for_message(author=user)

        minutesStartTime = int(start_time_Message.content.split(':')[0])
        secondsStartTime = int(start_time_Message.content.split(':')[1])
        startTimeMS = ((minutesStartTime * 60) + secondsStartTime) * 1000

        minutesEndTime = int(end_time_Message.content.split(':')[0])
        secondsEndTime = int(end_time_Message.content.split(':')[1])
        endTimeMS = ((minutesEndTime * 60) + secondsEndTime) * 1000

        # downloadThread.join()
        fullYTMp3 = async_result.get()
        pool.close()
        pool.join()
        print (str(endTimeMS))
        print (str(startTimeMS))
        print (str(endTimeMS - startTimeMS))

        if(endTimeMS - startTimeMS <= 6000):
            newSegment = fullYTMp3[startTimeMS:endTimeMS]

            newJoinMp3 = newSegment + joinMp3
            newLeaveMp3 = newSegment + leaveMp3

            os.chdir("/root/python/tts/join")
            newJoinMp3.export(user.name + ".mp3", format="mp3")
            os.chdir("/root/python/tts/leave")
            newLeaveMp3.export(user.name + ".mp3", format="mp3")

            await bot.send_message(user, "Successfully changed")
        else:
            await bot.send_message(user, "Greater than 5 seconds, fuck you for trying to break the bot")

        os.chdir("/root/python")

    except Exception as err:
        e = sys.exc_info()[0]
        traceback.print_tb(err.__traceback__)
        print ("This happened [ytdl]: " + str(e))

def youTubeVideoDownload(url):
    os.chdir("/root/python/youtubeMp3s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
            }],
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        #ydl.download([url])
        info_dict = ydl.extract_info(url, download=True)
        video_url = info_dict.get("url", None)
        video_id = info_dict.get("id", None)
        video_title = info_dict.get('title', None)

    fileName = "*-" + video_id + ".mp3"
    for file in glob.glob(fileName):
        print ("It's there")
        fullYTMp3 = AudioSegment.from_mp3(file)

    os.chdir("/root/python")
    return fullYTMp3 #for threading purposes

@bot.event
async def on_message(message):
    if(message.author.id in bannedUsers):
        upperCase = ''
    else:
        upperCase = message.content.upper()

    SmoothMember = bot.get_server("357558224288874496").get_member("185522982989463552")

    if(upperCase == "!TTS REDUCE" and message.channel.is_private):
        fileName = message.author.name + ".mp3"

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python")

        await bot.send_message(message.author, "Type the amount of db to reduce TTS by")
        reduceByMessage = await bot.wait_for_message(author=message.author)

        reduceAmount = int(reduceByMessage.content)

        joinTTSNew = joinTTS - reduceAmount
        leaveTTSNew = leaveTTS - reduceAmount

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTSNew.export(message.author.name + ".mp3", format="mp3")

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTSNew.export(message.author.name + ".mp3", format="mp3")

        await bot.send_message(message.author, "Success decreased")

    elif(upperCase == "!TTS INCREASE" and message.channel.is_private):
        fileName = message.author.name + ".mp3"

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTS = AudioSegment.from_mp3(file)

        os.chdir("/root/python")

        await bot.send_message(message.author, "Type the amount of db to increase TTS by")
        increaseByMessage = await bot.wait_for_message(author=message.author)

        increaseAmount = int(increaseByMessage.content)

        joinTTSNew = joinTTS + increaseAmount
        leaveTTSNew = leaveTTS + increaseAmount

        os.chdir("/root/python/tts/join")
        for file in glob.glob(fileName):
            joinTTSNew.export(message.author.name + ".mp3", format="mp3")

        os.chdir("/root/python/tts/leave")
        for file in glob.glob(fileName):
            leaveTTSNew.export(message.author.name + ".mp3", format="mp3")

        await bot.send_message(message.author, "Successfully increased")

    elif(upperCase.startswith('!TTS', 0, 4) and message.channel.is_private):
        await youtube_download(message.content, message.author)

@bot.event
async def on_voice_state_update(memberBefore, memberAfter):
    await bot.wait_until_ready()

    os.chdir("/root/python")
    if (os.stat(DATABASE_LOCATION).st_size != 0): #file not empty
        json_data = open(DATABASE_LOCATION).read()
        data = json.loads(json_data, object_pairs_hook=OrderedDict)

        lobbyVoiceChannel = bot.get_channel(LOBBY_VOICE_CHANNEL_ID)
        bigGameVoiceChannel = bot.get_channel(THE_GAME_VOICE_CHANNEL_ID)
        anotherGameVoiceChannel = bot.get_channel(ANOTHER_GAME_VOICE_CHANNEL_ID)
        botTestingChannel = bot.get_channel(BOTTESTING_CHANNEL_ID)
        state = Music.get_voice_state(memberAfter.server)

        if(memberBefore.voice.voice_channel != lobbyVoiceChannel and memberAfter.voice.voice_channel == lobbyVoiceChannel and memberBefore.top_role.name != "%bot"):
            if(memberAfter.name in data['Users']):
                if(memberBefore.id not in bannedUsers):
                    fileName = TTS_JOIN_FILES_LOCATION + memberAfter.name + '.mp3'
                else:
                    fileName = '/root/python/tts/' + EMPTY  + '.mp3'

                if(not os.path.isfile(fileName)):
                    print ("Error " + fileName + "does not exist")

                try:
                    if(state.voice is None):
                        await Music.join(lobbyVoiceChannel)
                        state.voice.poll_voice_ws()
                        print ("type of [user]: " + str(memberBefore.name))
                        print ("type of [state]: " + str(type(state)))
                        print ("type of [state.voice]: " + str(type(state.voice)))
                        print ("type of [Music.voice_states[DUCKWAD_SERVER_ID]]: " + str(type(Music.voice_states[DUCKWAD_SERVER_ID])))
                    await Music.play(memberAfter, fileName)
                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [Joining Lobby]: " + str(e))

        if(memberBefore.voice.voice_channel == lobbyVoiceChannel and memberAfter.voice.voice_channel != lobbyVoiceChannel):
            if ((state is not None) and (len(lobbyVoiceChannel.voice_members) == 1 and (bot.user in lobbyVoiceChannel.voice_members))):
                await Music.disconnect(memberAfter.server)
            elif(memberBefore.name in data['Users'] and memberBefore.top_role.name != "%bot"):
                fileName = TTS_LEAVE_FILES_LOCATION + memberAfter.name + '.mp3'
                try:
                    #await announceTTS.summon(memberAfter)
                    if(state.voice is None):
                        await Music.join(lobbyVoiceChannel)
                        state.voice.poll_voice_ws()
                        print ("type of [user]: " + str(memberBefore.name))
                        print ("type of [state]: " + str(type(state)))
                        print ("type of [state.voice]: " + str(type(state.voice)))
                        print ("type of [Music.voice_states[DUCKWAD_SERVER_ID]]: " + str(type(Music.voice_states[DUCKWAD_SERVER_ID])))
                    await Music.play(memberBefore, fileName)

                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [Leaving Lobby]: " + str(e))

        if(memberBefore.voice.voice_channel != bigGameVoiceChannel and memberAfter.voice.voice_channel == bigGameVoiceChannel and memberBefore.top_role.name != "%bot"):
            if(memberAfter.name in data['Users']):
                if(memberBefore.id not in bannedUsers):
                    fileName = TTS_JOIN_FILES_LOCATION + memberAfter.name + '.mp3'
                else:
                    fileName = '/root/python/tts/' + EMPTY  + '.mp3'

                if(not os.path.isfile(fileName)):
                    print ("Error " + fileName + "does not exist")

                try:
                    if(state.voice is None):
                        await Music.join(bigGameVoiceChannel)
                        state.voice.poll_voice_ws()
                        print ("type of [user]: " + str(memberBefore.name))
                        print ("type of [state]: " + str(type(state)))
                        print ("type of [state.voice]: " + str(type(state.voice)))
                        print ("type of [Music.voice_states[DUCKWAD_SERVER_ID]]: " + str(type(Music.voice_states[DUCKWAD_SERVER_ID])))
                    await Music.play(memberAfter, fileName)
                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [Joining Lobby]: " + str(e))

        if(memberBefore.voice.voice_channel == bigGameVoiceChannel and memberAfter.voice.voice_channel != bigGameVoiceChannel):
            if ((state is not None) and (len(bigGameVoiceChannel.voice_members) == 1 and (bot.user in bigGameVoiceChannel.voice_members))):
                await Music.disconnect(memberAfter.server)
            elif(memberBefore.name in data['Users'] and memberBefore.top_role.name != "%bot"):
                fileName = TTS_LEAVE_FILES_LOCATION + memberAfter.name + '.mp3'
                try:
                    #await announceTTS.summon(memberAfter)
                    if(state.voice is None):
                        await Music.join(bigGameVoiceChannel)
                        state.voice.poll_voice_ws()
                        print ("type of [user]: " + str(memberBefore.name))
                        print ("type of [state]: " + str(type(state)))
                        print ("type of [state.voice]: " + str(type(state.voice)))
                        print ("type of [Music.voice_states[DUCKWAD_SERVER_ID]]: " + str(type(Music.voice_states[DUCKWAD_SERVER_ID])))
                    await Music.play(memberBefore, fileName)

                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [Leaving Lobby]: " + str(e))

        if(memberBefore.voice.voice_channel != anotherGameVoiceChannel and memberAfter.voice.voice_channel == anotherGameVoiceChannel and memberBefore.top_role.name != "%bot"):
            if(memberAfter.name in data['Users']):
                if(memberBefore.id not in bannedUsers):
                    fileName = TTS_JOIN_FILES_LOCATION + memberAfter.name + '.mp3'
                else:
                    fileName = '/root/python/tts/' + EMPTY  + '.mp3'

                if(not os.path.isfile(fileName)):
                    print ("Error " + fileName + "does not exist")

                try:
                    if(state.voice is None):
                        await Music.join(anotherGameVoiceChannel)
                        state.voice.poll_voice_ws()
                        print ("type of [user]: " + str(memberBefore.name))
                        print ("type of [state]: " + str(type(state)))
                        print ("type of [state.voice]: " + str(type(state.voice)))
                        print ("type of [Music.voice_states[DUCKWAD_SERVER_ID]]: " + str(type(Music.voice_states[DUCKWAD_SERVER_ID])))
                    await Music.play(memberAfter, fileName)
                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [Joining Lobby]: " + str(e))

        if(memberBefore.voice.voice_channel == anotherGameVoiceChannel and memberAfter.voice.voice_channel != anotherGameVoiceChannel):
            if ((state is not None) and (len(anotherGameVoiceChannel.voice_members) == 1 and (bot.user in anotherGameVoiceChannel.voice_members))):
                await Music.disconnect(memberAfter.server)
            elif(memberBefore.name in data['Users'] and memberBefore.top_role.name != "%bot"):
                fileName = TTS_LEAVE_FILES_LOCATION + memberAfter.name + '.mp3'
                try:
                    #await announceTTS.summon(memberAfter)
                    if(state.voice is None):
                        await Music.join(anotherGameVoiceChannel)
                        state.voice.poll_voice_ws()
                        print ("type of [user]: " + str(memberBefore.name))
                        print ("type of [state]: " + str(type(state)))
                        print ("type of [state.voice]: " + str(type(state.voice)))
                        print ("type of [Music.voice_states[DUCKWAD_SERVER_ID]]: " + str(type(Music.voice_states[DUCKWAD_SERVER_ID])))
                    await Music.play(memberBefore, fileName)

                except discord.ClientException:
                    print ('client exception')
                    pass
                except Exception as err:
                    e = sys.exc_info()[0]
                    traceback.print_tb(err.__traceback__)
                    print ("This happened [Leaving Lobby]: " + str(e))

@bot.event
async def on_ready():
    database = dataBase_check()
    print('Logged in as:\n{0} (ID: {0.id})'.format(bot.user))

Music = Music(bot)
bot.run(token)
