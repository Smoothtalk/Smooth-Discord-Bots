import discord
import asyncio
import os
import sys
import reconnecting_bot
import aiohttp
import requests
import websockets

BOTTESTING_CHANNEL_ID = ""
DUCKWAD_SERVER_ID = ""
BEAR_ID = ''
SMOOTH_ID = ''
LOOP_SECONDS = 60
SERVER_IP = '192.168.2.29'
SERVER_PORT = '3000'
SERVER_API = '/statuschange'
#6 per minute

token = ''

discordClient = discord.Client()

@discordClient.event
async def on_member_update(memberBefore, memberAfter):
    await discordClient.wait_until_ready()
    if(memberAfter.id == BEAR_ID):
        if(memberAfter.status is discord.Status.online):
            isDead = False
        else:
            isDead = True
        r = requests.post('http://192.168.2.29:3000/statuschange', data = {'isDead': isDead})
        print ('bear change')

@discordClient.event
async def on_ready():
    print('Logged in as')
    print(discordClient.user.name)
    print(discordClient.user.id)
    duckServer = discordClient.get_server(DUCKWAD_SERVER_ID)
    duckServerUsers = duckServer.members

    bear = discord.utils.find(lambda m: m.id == BEAR_ID, duckServerUsers)
    if(bear.status is discord.Status.online):
        isDead = False
    else:
        isDead = True
    r = requests.post('http://' + SERVER_IP + ':' + SERVER_PORT + SERVER_API, data = {'isDead': isDead})
    print('-----')

asyncio.get_event_loop().run_until_complete(reconnecting_bot.keep_running(discordClient, token))
discordClient.run(token)

# try:
#     duckServer = discordClient.get_server(DUCKWAD_SERVER_ID)
#     duckServerUsers = duckServer.members
#     for discord.Member in duckServerUsers:
#         if discord.Member.id == BEAR_ID:
#             bear = discord.Member
#             if bear.status is discord.Status.idle or bear.status is discord.Status.offline or bear.status is discord.Status.dnd:
#
#
# except:
#     e = sys.exc_info()[0]
#     print ("This happened: " + str(e))
#     if discordClient.is_closed:
#         discordClient._closed.clear()
#         discordClient.http.recreate()
#     try:
#         await discordClient.connect()
#     except (discord.HTTPException, aiohttp.ClientError,
#             discord.GatewayNotFound, discord.ConnectionClosed,
#             websockets.InvalidHandshake,
#             websockets.WebSocketProtocolError) as e:
#         if isinstance(e, discord.ConnectionClosed) and e.code == 4004:
#             raise # Do not reconnect on authentication failure
#         logging.exception("Discord.py pls keep running")
#
# await asyncio.sleep(LOOP_SECONDS)
