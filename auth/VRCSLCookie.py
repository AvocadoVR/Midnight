import json
import base64
from http.cookiejar import Cookie
import os
import vrchatapi
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Build absolute path to cookie file
COOKIE_FILE = os.path.join(SCRIPT_DIR, "./cookie.json")

CODE = os.getenv("ENCRYPT")
key = Fernet(CODE)


def make_cookie(name: str, value: str) -> Cookie:
    return Cookie(
        0, name, value,
        None, False,
        "api.vrchat.cloud", True, False,
        "/", False,
        False,
        173106866300,
        False,
        None,
        None, {}
    )


def get_auth_cookie() -> str | None:
    if not os.path.exists(COOKIE_FILE):
        print("Cookie file does not exist.")
        return None

    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        auth_value = cookies.get("auth")
        if not auth_value:
            print("No 'auth' key found in cookie file.")
            return None

        cookie_auth = key.decrypt(base64.b64decode(auth_value)).decode()
        return cookie_auth

    except Exception as e:
        print(f"Error loading cookie: {e}")
        return None


def save_cookies(api_client: vrchatapi.ApiClient):
    """Saves the authentication cookies to a file."""
    try:
        cookie_jar = api_client.rest_client.cookie_jar._cookies["api.vrchat.cloud"]["/"]
        cookies = {
            "auth": base64.b64encode(key.encrypt(cookie_jar["auth"].value.encode())).decode(),
            "twoFactorAuth": base64.b64encode(key.encrypt(cookie_jar["twoFactorAuth"].value.encode())).decode(),
        }
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            json.dump(cookies, f)
        print(f"Cookies saved to {COOKIE_FILE}")
    except Exception as e:
        print(f"Error saving cookies: {e}")


def load_cookies(api_client: vrchatapi.ApiClient) -> bool:
    """Loads authentication cookies from a file."""
    if not os.path.exists(COOKIE_FILE):
        return False
    try:
        with open(COOKIE_FILE, "r", encoding="utf-8") as f:
            cookies = json.load(f)

        cookie_auth = key.decrypt(base64.b64decode(cookies.get("auth"))).decode()
        cookie_two_factor = key.decrypt(base64.b64decode(cookies.get("twoFactorAuth"))).decode()

        if cookie_auth:
            api_client.rest_client.cookie_jar.set_cookie(make_cookie("auth", cookie_auth))
        if cookie_two_factor:
            api_client.rest_client.cookie_jar.set_cookie(make_cookie("twoFactorAuth", cookie_two_factor))

        print("Cookies loaded from file.")
        return True
    except Exception as e:
        print(f"Error loading cookies: {e}")
        return False
