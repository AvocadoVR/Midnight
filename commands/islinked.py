import discord
from discord import app_commands
from discord.ext import commands

from Database import get_verified_user


class IsLinked(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="islinked",
        description="Checks if a user's account is linked"
    )
    @app_commands.describe(member="The member to check. Leave empty to check yourself.")
    async def islinked(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
    ):
        await interaction.response.defer(ephemeral=True)

        # Default to the command user if no member is provided
        member = member or interaction.user

        discordId = member.id

        is_verified_user = await get_verified_user(discordId=discordId)

        embed = discord.Embed(
            title=f"{member.display_name}'s Verification Status",
            color=discord.Color.green() if is_verified_user else discord.Color.red()
        )

        if is_verified_user:
            embed.description = "✅ This VRChat account is linked."
        else:
            embed.description = "❌ This user does not have a linked VRChat account."

        embed.set_thumbnail(url=member.display_avatar.url)

        await interaction.followup.send(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(IsLinked(bot))
