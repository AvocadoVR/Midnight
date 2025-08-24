import discord
from discord import app_commands
from discord.ext import commands

from Database import get_pending_verification, get_verified_user, remove_pending_verification, add_verified_user, \
    remove_verified_user
from api.VRCApi import get_user_by_id

class Forcelink(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="forcelink", description="Checks the status of users")
    @app_commands.describe(vrchat_profile="UserID or URL of VRChat profile",
                           discord_member="Select user to forcelink with the VRChat Profile",
                           override_unlink="To override unlink cooldown.")
    async def forcelink(self, interaction: discord.Interaction, discord_member: discord.Member, vrchat_profile: str, override_unlink: bool):
        await interaction.response.defer(ephemeral=True)

        vrchatId = vrchat_profile.split("/")[-1]
        discordId = discord_member.id

        hasPendingVerification = await get_pending_verification(discordId=discordId)
        hasBeenVerified = await get_verified_user(discordId=discordId)

        if hasPendingVerification:
            await remove_pending_verification(discordId=discordId)
            await interaction.followup.send("Cancelled Pending Verification.", ephemeral=True)

        if hasBeenVerified and not override_unlink:
            await interaction.followup.send("They are already verified. They have to unlink their account.", ephemeral=True)
            return
        elif hasBeenVerified and override_unlink:
            await remove_verified_user(discordId=discordId)
            await interaction.followup.send(
                f"Overriding unlink cooldown for {discord_member.name} and removing old link.",
                ephemeral=True
            )

        user = await get_user_by_id(vrchatId=vrchatId)

        isAgeVerified = getattr(user, "age_verified", None)

        if user is None:
            await interaction.followup.send("Invalid VRChat Profile!", ephemeral=True)
            return

        if isAgeVerified:
            await interaction.followup.send(f"VRChat account successfully linked to {discord_member.mention}!", ephemeral=True)
            await add_verified_user(discordId=discordId, vrchatId=vrchatId)
        else:
            await interaction.followup.send("They are not age verified on VRChat.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Forcelink(bot))
