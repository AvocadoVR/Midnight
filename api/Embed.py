import discord


def Bad_Credentials_Embed() -> discord.Embed:
    return discord.Embed(
        title="Bad Credentials",
        description="Please update authentication",
        color=discord.Color.red()
    )

def Group_Missing_Embed() -> discord.Embed:
    return discord.Embed(
        title="Group Missing",
        description="Please update authentication",
        color=discord.Color.red()
    )


def VRC_Join_Request_Embed(sender: str, request_message: str, bio: str, image_url: str, age_verified_text: str, dateJoined: str) -> discord.Embed:
    embed = discord.Embed(
        title=f"Join Request - {sender}",
        description=f"{request_message}\n\n**Bio**\n{bio}",
        color=discord.Color.dark_gold(),
    )

    embed.add_field(name="Age Verified", value=age_verified_text, inline=True)
    embed.add_field(name="Date Joined", value=dateJoined, inline=True)

    if image_url:
        embed.set_thumbnail(url=image_url)

    return embed


def Verfication_Embed(code: str, vrchat_profile: str) -> discord.Embed:
    embed = discord.Embed(
        title="🔗 VRChat Account Linking",
        description=(
            f"Your verification code is:\n**`{code}`**\n\n"
            "You must be 18+ Verified on VRChat. No exceptions\n You have 2 minutes to complete this before this code expires.\n"
            "1. Copy this code.\n"
            "2. Paste it into your VRChat **bio**.\n"
            "3. Once done, click the button below to verify."
        ),
        color=discord.Color.blue(),
    )

    embed.add_field(name="VRChat Profile", value=f"[Click to view profile]({vrchat_profile})", inline=False)

    return embed
