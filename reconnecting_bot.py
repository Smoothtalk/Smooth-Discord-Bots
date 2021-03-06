import logging
import asyncio
import aiohttp
import discord
import websockets

import backoff

async def keep_running(client, token):
    retry = backoff.ExponentialBackoff()

    while True:
        try:
            await client.login(token)

        except (discord.HTTPException, aiohttp.ClientError):
            logging.exception("Discord.py pls login")
            await asyncio.sleep(retry.delay())

        else:
            break

    while client.is_logged_in:
        if client.is_closed:
            client._closed.clear()
            client.http.recreate()

        try:
            await client.connect()

        except (discord.HTTPException, aiohttp.ClientError,
                discord.GatewayNotFound, discord.ConnectionClosed,
                websockets.InvalidHandshake,
                websockets.WebSocketProtocolError) as e:
            if isinstance(e, discord.ConnectionClosed) and e.code == 4004:
                raise # Do not reconnect on authentication failure
            logging.exception("Discord.py pls keep running")
            await asyncio.sleep(retry.delay())


#logging.basicConfig(level=logging.INFO)
# client = discord.Client()
# token = '<token>'
# asyncio.get_event_loop().run_until_complete(keep_running(client, token))
