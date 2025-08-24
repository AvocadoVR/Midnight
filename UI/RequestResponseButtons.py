import discord
from api.VRCApi import group_request_response

class RequestResponseButtons(discord.ui.View):
    def __init__(self, senderName: str, senderId: str):
        super().__init__()
        self.senderName = senderName
        self.senderId = senderId

    async def disable_buttons(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await interaction.message.edit(view=self)

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        await group_request_response(vrchatId=self.senderId, isAccepted=True)
        discordUser = interaction.user

        await interaction.response.send_message(
            f"✅ {discordUser.mention} approved **{self.senderName}**’s request to join the group!"
        )
        await self.disable_buttons(interaction)

    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        await group_request_response(vrchatId=self.senderId, isAccepted=False)
        discordUser = interaction.user

        await interaction.response.send_message(
            f"❌ {discordUser.mention} rejected **{self.senderName}**’s request to join the group."
        )
        await self.disable_buttons(interaction)
