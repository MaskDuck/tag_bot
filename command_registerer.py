import requests

from os import environ

appid = environ['client_id']
token = environ['token']
guild = environ['guild_id']

url = f"https://discord.com/api/v10/applications/{appid}/guilds/{guild}/commands/"

headers = {"Authorization": f"Bot {token}"}

json = {
    "name": "tag",
    "type": 1,
    "description": "new tag",
}

r = requests.post(url, headers=headers, json=json)
