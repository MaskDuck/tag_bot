from pymongo import MongoClient

from flask import Flask, jsonify, request, Response

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from typing import Final
from os import environ
import requests

debug = False
if debug:
    from dotenv import load_dotenv

    load_dotenv()

app = Flask(__name__)
public_key: str = environ["public_key"]
verify_key: VerifyKey = VerifyKey(bytes.fromhex(public_key))
appid = environ["client_id"]
token = environ["token"]
guild = environ["guild_id"]

url: Final[
    str
] = f"https://discord.com/api/v8/applications/{appid}/guilds/{guild}/commands"
mongo: MongoClient = MongoClient(environ["mongo"])["dev"]["storer"]

maintainers: Final[list[int]] = [
    716134528409665586,  # MaskDuck
    911987862981972058,  # Hackermon
    763767239018938368,  # molai
    730358289849778186,  # phenax
    488802888928329753,  # Botly
]


@app.route("/", methods=["POST"])
async def handler():
    verified = False
    # validating signatures
    try:
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
        body = request.data.decode("utf-8")
        verify_key.verify(f"{timestamp}{body}".encode(), bytes.fromhex(signature))
        verified: bool = True
    except BadSignatureError:
        verified: bool = False
        return Response(status=401)
    if verified:
        data: dict = request.get_json()
        if data["type"] == 1:
            return jsonify({"type": 1})
        elif data["type"] == 2:
            if data["data"]["name"] == "tag":
                if int(data["member"]["user"]["id"]) in maintainers:
                    modal = {
                        "title": "New Tag",
                        "custom_id": "TAG_Modal",
                        "components": [
                            {
                                "type": 1,
                                "components": [
                                    {
                                        "type": 4,
                                        "custom_id": "TAG_Modal_Name",
                                        "style": 1,
                                        "label": "Tag Name",
                                        "max_length": 32,
                                        "placeholder": "If you are editing a tag please give the tag name here.",
                                    }
                                ],
                            },
                            {
                                "type": 1,
                                "components": [
                                    {
                                        "type": 4,
                                        "custom_id": "TAG_Modal_Content",
                                        "style": 2,
                                        "label": "Tag Content",
                                        "max_length": 1999,
                                        "placeholder": "Leave this part as blank to delete this tag.",
                                        "required": False
                                    }
                                ],
                            },
                        ],
                    }
                    return jsonify({"type": 9, "data": modal})
                else:
                    return jsonify(
                        {
                            "type": 4,
                            "data": {
                                "content": "You do not have permission to use this command.",
                                "flags": 1 << 6,
                            },
                        }
                    )
            elif data["data"]["name"] == "ping":
                return jsonify({"type": 4, "data": {"content": "pong"}})
            else:
                existing_data = mongo.find_one({"_id": data["data"]["name"]})
                return jsonify(
                    {"type": 4, "data": {"content": existing_data["content"]}}
                )
        elif data["type"] == 5:
            if data["data"]["custom_id"] == "TAG_Modal":
                existing_data = mongo.find_one(
                    {"_id": data["data"]["components"][0]["components"][0]["value"]}
                )
                editing = False
                if existing_data:
                    editing = True
                if editing:
                    mongo.update_one(
                        {
                            "_id": data["data"]["components"][0]["components"][0][
                                "value"
                            ]
                        },
                        {
                            "$set": {
                                "content": data["data"]["components"][1]["components"][
                                    0
                                ]["value"]
                            }
                        },
                    )
                    return jsonify({"type": 4, "data": {"content": "Tag updated."}})
                else:
                    insert_data = {
                        "_id": data["data"]["components"][0]["components"][0]["value"],
                        "content": data["data"]["components"][1]["components"][0][
                            "value"
                        ],
                    }
                    mongo.insert_one(insert_data)
                    json = {
                        "name": data["data"]["components"][0]["components"][0]["value"],
                        "type": 1,
                        "description": "custom tag",
                    }
                    headers = {"Authorization": f"Bot {token}"}
                    requests.post(url, headers=headers, json=json)
                    return jsonify(
                        {
                            "type": 4,
                            "data": {
                                "content": f"Created a tag with name {data['data']['components'][0]['components'][0]['value']} and content {data['data']['components'][1]['components'][0]['value']}. To edit the tag please contact MaskDuck."
                            },
                        }
                    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
