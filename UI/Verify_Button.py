import os

import discord

from Database import get_pending_verification, add_verified_user, remove_pending_verification
from api.VRCApi import get_user_by_id

VERIFIED_ROLE = os.getenv('VERIFIED_ROLE')

class VerifyButton(discord.ui.View):
    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green)
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        discordId = interaction.user.id

        verification = await get_pending_verification(discordId=discordId)

        if verification is None:
            await interaction.response.send_message("You don't have any pending verification", ephemeral=True)
            return

        vrchatId = verification.vrchatId

        user = await get_user_by_id(vrchatId=vrchatId)

        isAgeVerified = getattr(user, "age_verified", None)
        bio = getattr(user, "bio", None)

        if user is None:
            await interaction.response.send_message("Invalid VRChat Profile!", ephemeral=True)
            return

        isBio = verification.code in bio

        if not isBio and not isAgeVerified:
            await interaction.response.send_message("There was no code found. You're also not age verified!", ephemeral=True)
            return
        elif not isAgeVerified:
            await interaction.response.send_message("You're not age verified!", ephemeral=True)
            return
        elif not isBio:
            await interaction.response.send_message("There was no code found.", ephemeral=True)
            return
        else:
            await interaction.response.send_message("Verification Successful!", ephemeral=True)

        await remove_pending_verification(discordId=discordId)

        await add_verified_user(discordId=discordId, vrchatId=vrchatId)

        role = interaction.guild.get_role(int(VERIFIED_ROLE))

        await interaction.user.add_roles(role)