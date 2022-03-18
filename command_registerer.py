"""
This file is used for registering commands.
"""
import requests

from os import environ

from dotenv import load_dotenv

load_dotenv()

appid = environ["client_id"]
token = environ["token"]
guild = environ["guild_id"]

url = f"https://discord.com/api/v8/applications/{appid}/guilds/{guild}/commands"


headers = {"Authorization": f"Bot {token}"}

json = {
    "name": "tag",
    "type": 1,
    "description": "[MAINTAINER ONLY] new tag, or edit a existing tag.",
}

r = requests.post(url, headers=headers, json=json)
print(r.status_code)
