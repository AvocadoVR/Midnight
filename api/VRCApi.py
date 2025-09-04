from typing import List, Optional

import pyotp
import vrchatapi

from dotenv import load_dotenv
import os

from vrchatapi import TwoFactorAuthCode, UsersApi, GroupsApi, RespondGroupJoinRequest, \
    CreateGroupInviteRequest, ApiException, CalendarEvent, CalendarApi
from vrchatapi.api import authentication_api, groups_api
from vrchatapi.exceptions import UnauthorizedException, NotFoundException

from auth.VRCSLCookie import load_cookies, save_cookies

load_dotenv()

Username = os.getenv("VRC_USER")
Password = os.getenv("VRC_PASS")
VRC_KEY = os.getenv("VRC_KEY")
Group_ID = os.getenv("GROUP_ID")
Bot_Log = os.getenv("BOT_LOG_CHANNEL")

totp = pyotp.TOTP(VRC_KEY)

configuration = vrchatapi.Configuration(
    username = Username,
    password = Password,
)

with vrchatapi.ApiClient(configuration) as api_client:
    logged_in = False

    api_client.user_agent = "MidnightBot/2.0 midnightserenade2025@gmail.com"


    auth_api = authentication_api.AuthenticationApi(api_client)

    # 1. Try to load cookies from file
    if load_cookies(api_client):
        try:
            current_user = auth_api.get_current_user()
            print(f"Logged in with cookies as {current_user.display_name}")
            logged_in = True
        except (UnauthorizedException, vrchatapi.ApiException):
            print("Stored cookies invalid, performing fresh login.")

    # 2. If cookies are missing or invalid, login normally
    if not logged_in:
        try:
            print()
            current_user = auth_api.get_current_user()
        except UnauthorizedException as e:
            if e.status == 200:
                if "2 Factor Authentication" in e.reason:
                    auth_api.verify2_fa(
                        two_factor_auth_code=TwoFactorAuthCode(totp.now())
                    )

                current_user = auth_api.get_current_user()
            else:
                print(f"Exception when calling API: {e}")
        except vrchatapi.ApiException as e:
            print(f"Exception when calling API: {e}")

    save_cookies(api_client)

    users_api = UsersApi(api_client)
    group_api = GroupsApi(api_client)
    calendar_api = CalendarApi(api_client)



async def get_user_by_id(vrchatId: str):
    try:
        userData = users_api.get_user(vrchatId)

        if userData and getattr(userData, "id", None) == vrchatId:
            return userData
        return None

    except UnauthorizedException as e:
        print(f"Unauthorized: {e}")
        return None
    except NotFoundException:
        print("User not found.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# https://vrchat.community/openapi/respond-group-join-request

async def group_request_response(vrchatId: str, isAccepted: bool) -> bool:
    try:
        action = "accept" if isAccepted else "reject"
        request = RespondGroupJoinRequest(action=action)

        group_api.respond_group_join_request(Group_ID, vrchatId, request)

        return True
    except ApiException as e:
        print(e)
        return False


# https://vrchat.community/openapi/get-group-requests

async def get_pending_invites():
    try:
        pendingInvites = group_api.get_group_requests(Group_ID)

        return pendingInvites
    except ApiException as e:
        print(e)
        return None

async def get_vrchat_events() -> List[bool] | None:
    try:
        vrchatEvents = calendar_api.get_group_calendar_events(Group_ID)




    except (UnauthorizedException, NotFoundException) as e:
        print(f"Unauthorized: {e}")

    title = None
    description = None
    startsAt = None
    endsAt = None

    pass

async def add_vrchat_event(title: str, description: str, startsAt: str, endsAt: str):
    pass


