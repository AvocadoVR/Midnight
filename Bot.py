import asyncio
from datetime import datetime, timedelta

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


LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_filename = datetime.now().strftime("logs/bot_%Y-%m-%d.log")

handler = logging.FileHandler(filename=log_filename, encoding="utf-8", mode="a")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[handler]
)

def cleanup_old_logs(days=5):
    today = datetime.now().date()  # only the date
    for file in os.listdir(LOG_DIR):
        file_path = os.path.join(LOG_DIR, file)
        if os.path.isfile(file_path):
            file_date = datetime.fromtimestamp(os.path.getmtime(file_path)).date()
            if today - file_date > timedelta(days=days):
                try:
                    os.remove(file_path)
                    print(f"Deleted old log: {file}")
                except Exception as e:
                    print(f"Failed to delete {file}: {e}")

intents = discord.Intents.all()
intents.message_content = True
intents.members = True


class Midnight(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=None, intents=intents)

    async def setup_hook(self):
        cleanup_old_logs()

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
midnight.run(BOT_TOKEN)
