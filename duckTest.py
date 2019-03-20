import asyncio
import os
import random
import datetime
import discord

token = ""
DUCKWAD_SERVER_ID = ""
LOBBY_CHANNEL_ID = ""
BOTTESTING_CHANNEL_ID = ""
USER_DUCKWAD_ID = ""
USER_SMOOTHTALK_ID = ""
#HALF_LIFE_SIREN_URL = "https://www.youtube.com/watch?v=wAqnrpDwaCM"

discordClient = discord.Client()

#0 is player, 1 is requester. {0,1}
class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = 'Testing voice for {1.display_name}'
        return fmt.format(self.player, self.requester) #tuple found here

class VoiceState:
    def __init__(self, discordClient):
        self.voice = None
        self.discordClient = discordClient
        self.is_done = False

    async def play_horn(self, package):
        await self.discordClient.send_message(package.channel, str(package))
        package.player.start()

        while(package.player.is_playing()):
            self.is_done = False

        if(package.player.is_playing() == False):
            self.is_done = True

@discordClient.event
async def on_message(message):
    upperCase = message.content.upper()
    testingChannel = discordClient.get_channel(BOTTESTING_CHANNEL_ID)
    if (upperCase.startswith('!VTEST', 0, 6) and (message.author.id == USER_DUCKWAD_ID or message.author.id == USER_SMOOTHTALK_ID)):
        try:
            summoned_channel = message.author.voice_channel
            if summoned_channel is None:
                await discordClient.send_message(message.channel, 'You are not in a voice channel.')
                return False
            state = VoiceState(discordClient)

            if state.voice is None:
                state.voice = await discordClient.join_voice_channel(summoned_channel)
            else:
                await state.voice.move_to(summoned_channel)

            try:
                opts = {
                    'quiet': True,
                }
                player = state.voice.create_ffmpeg_player("videos/horn.mp4", options=opts)
            except Exception as e:
                fmt = 'An inner error occurred while processing this request: ```py\n{}: {}\n```'
                await discordClient.send_message(message.channel, fmt.format(type(e).__name__, e))
            else:
                player.volume = 0.2
                package = VoiceEntry(message, player)
                await state.play_horn(package)

                if (state.is_done):
                    await state.voice.disconnect()

        except Exception as e:
            fmt = 'An outer error occurred while processing this request: ```py\n{}: {}\n```'
            await discordClient.send_message(message.channel, fmt.format(type(e).__name__, e))
    elif((upperCase.startswith('!VTEST', 0, 6)) and not(message.author.id == USER_DUCKWAD_ID or message.author.id == USER_SMOOTHTALK_ID)):
        await discordClient.send_message(message.channel, 'You are not a valid user')

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    print('-------')

discordClient.run(token)
