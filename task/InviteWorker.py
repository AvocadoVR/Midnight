import asyncio

from Database import get_invite_list
from api.VRCApi import invite_to_group


async def invite_worker():
    invites = get_invite_list()

    invite = invites[0]

    if not invites:
        return
    else:
        status = await invite_to_group(invite.vrchatId)

