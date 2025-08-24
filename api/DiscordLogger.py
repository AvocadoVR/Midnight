import discord
import os

from dotenv import load_dotenv

load_dotenv()

LOG_CHANNEL = os.getenv("BOT_LOG_CHANNEL")

class DiscordLogger:
    instance = None

    def __init__(self, bot: discord.Client):
        self.bot = bot
        DiscordLogger.instance = self

    async def discordLog(self, embed: discord.Embed):

        channel =  self.bot.get_channel(int(LOG_CHANNEL))

        await channel.send(embed=embed)