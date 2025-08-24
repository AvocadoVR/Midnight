import asyncio

import discord
from discord.ext import commands, tasks

import logging

import os

from dotenv import load_dotenv

from Database import setup_db, remove_expired_verifications

from api.VRCListener import VRCListener
from auth.VRCSLCookie import get_auth_cookie

load_dotenv()

BOT_TOKEN = os.getenv('TOKEN')

WS_URL = os.getenv('WS_URL')
CHANNEL = int(os.getenv('GROUP_REQUEST_CHANNEL'))

handler = logging.FileHandler(filename="bot.log", encoding="utf-8", mode="w")

intents = discord.Intents.all()
intents.message_content = True
intents.members = True



class Midnight(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        for filename in os.listdir("./commands"):
            if filename.endswith(".py"):
                await self.load_extension(f"commands.{filename[:-3]}")
                print(f"Loaded {filename[:-3]}")

        await self.tree.sync()
        print("Slash commands synced.")



    async def on_ready(self):
        await setup_db()

        authCookie = get_auth_cookie()

        if authCookie:
            listener = VRCListener(midnight, WS_URL + authCookie, CHANNEL)

            asyncio.create_task(listener.listen())

        else:
            print("Listener failed.")


        self.check_expired_loop.start()
        #self.tick_invite_worker.start()

        print(f"{self.user} has connected to Discord!")


    @tasks.loop(seconds=30)
    async def check_expired_loop(self):
        await remove_expired_verifications()


midnight = Midnight()
midnight.run(BOT_TOKEN, log_handler=handler, log_level=logging.DEBUG)
