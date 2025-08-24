import random
import string

import discord
from discord import app_commands, Member
from discord.ext import commands

from Database import get_pending_verification, get_verified_user, remove_pending_verification, \
    create_pending_verification
from UI.Verify_Button import VerifyButton
from api.Embed import Verfication_Embed
from api.VRCApi import get_user_by_id


class Link(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="link", description="Link your VRChat to you're discord.")
    @app_commands.describe(
        vrchat_profile="UserID or URL of VRChat profile"
    )
    async def link(self, interaction: discord.Interaction, vrchat_profile: str):
        await interaction.response.defer(ephemeral=True)

        vrchatId = vrchat_profile.split("/")[-1]
        discordId = interaction.user.id

        hasPendingVerification = await get_pending_verification(discordId=discordId)
        hasBeenVerified = await get_verified_user(discordId=discordId)

        if hasPendingVerification:
            await remove_pending_verification(discordId=discordId)
            await interaction.followup.send(
                "You had an existing pending verification, which has now been cancelled. Please run the command again to start over.", ephemeral=True)
        elif hasBeenVerified:
            await interaction.followup.send(
                "You're already verified. If must do /unlink if you'd link a new account to your discord.", ephemeral=True)
            return

        code = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
        await create_pending_verification(interaction.user.id, vrchatId, code)

        embed = Verfication_Embed(code=code, vrchat_profile=vrchat_profile)

        verify = VerifyButton()

        await interaction.followup.send(embed=embed, view=verify, ephemeral=True)


async def setup(bot):
    await bot.add_cog(Link(bot))