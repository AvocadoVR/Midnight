import datetime

import discord
from discord import app_commands
from discord.ext import commands

from Database import get_verified_user, remove_verified_user


class Unlink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="unlink", description="Unlink your VRChat from you're discord.")
    @app_commands.describe(member="Select a member to unlink (Admin)")
    async def unlink(self, interaction: discord.Interaction, member: discord.Member = None):
        await interaction.response.defer(ephemeral=True)

        if interaction.user.guild_permissions.administrator and member:
            target = member
        else:
            target = interaction.user


        discordId = target.id

        isVerifiedUser = await get_verified_user(discordId=discordId)

        # Case 1: The user is not verified at all
        if not isVerifiedUser:
            await interaction.followup.send(
                "You are not currently verified, so there is no account to unlink.",
                ephemeral=True
            )
            return

        # Case 2: The user is verified, but they are on cooldown
        if isVerifiedUser.change_account > datetime.datetime.utcnow():
            formatted_date = isVerifiedUser.change_account.strftime("%A, %B %d, %Y")
            await interaction.followup.send(
                f"Your account is on cooldown. You can change it again on **{formatted_date}**. "
                f"If this is an emergency, please DM or mention a mod.",
                ephemeral=True
            )
            return

        # Case 3: The user is verified and the cooldown has expired
        # This is the only path that performs the unlink action.
        await remove_verified_user(discordId=discordId)
        await interaction.followup.send(
            f"Your VRChat account has been successfully unlinked. You'll have to wait 90 days to unlink again.",
            ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(Unlink(bot))