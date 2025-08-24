import asyncio
import json

import discord
import websockets

from UI.RequestResponseButtons import RequestResponseButtons
from api.Embed import VRC_Join_Request_Embed
from api.VRCApi import get_user_by_id


class VRCListener:
    def __init__(self, bot: discord.Client, ws_url: str, channel_id: int):
        self.ws_url = ws_url
        self.bot = bot
        self.channel_id = channel_id

    async def listen(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        }

        while True:
            try:
                async with websockets.connect(self.ws_url, extra_headers=headers) as websocket:

                    print(f"Connected to {self.ws_url}")

                    async for message in websocket:
                        await self.on_message(message)

            except Exception as e:
                print(f"WebSocket error: {e}. Reconnecting in 5s...")
                await asyncio.sleep(5)

    async def on_message(self, message):
        if isinstance(message, str):
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                return

        if message.get("type") != "notification-v2":
            return

        await self.parse_group_request(message)

    async def parse_group_request(self, message):

        content = json.loads(message['content'])

        if content["type"] == "group.joinRequest":

            sender = content["senderUsername"]
            senderId = content["senderUserId"]
            request_message = content["message"]
            image_url = content["imageUrl"]

            userData = await get_user_by_id(senderId)

            isAgeVerified = getattr(userData, "age_verified", False)
            dateJoined = getattr(userData, "date_joined", "Non-Existent")
            bio = getattr(userData, "bio", "")

            age_verified_text = "Yes" if isAgeVerified else "No"

            embed = VRC_Join_Request_Embed(sender, request_message, bio, image_url, age_verified_text, dateJoined)

            channel = self.bot.get_channel(self.channel_id)

            view = RequestResponseButtons(senderName=sender, senderId=senderId)

            await channel.send(embed=embed, view=view)
