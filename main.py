# from pymongo import MongoClient

from flask import Flask, jsonify, request, Response

from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

from os import environ

debug = False
if debug:
    from dotenv import load_dotenv
    load_dotenv()

app= Flask(__name__)
public_key: str = environ['public_key']
verify_key: VerifyKey = VerifyKey(bytes.fromhex(public_key))


# mongo: MongoClient = MongoClient(environ['mongo'])["dev"]["storer"]

maintainers: list[int] = [716134528409665586, 911987862981972058, 763767239018938368, 730358289849778186, 488802888928329753]

@app.route("/", methods=["POST"])
async def handler():
    verified = False
    # validating signatures
    try:
        signature = request.headers["X-Signature-Ed25519"]
        timestamp = request.headers["X-Signature-Timestamp"]
        body = request.data.decode("utf-8")
        verify_key.verify(f'{timestamp}{body}'.encode(), bytes.fromhex(signature))
        verified: bool = True
    except BadSignatureError:
        verified: bool = False
        return Response(status=401)
    if verified:
        data: dict = request.get_json()
        if data["type"] == 1:
            return jsonify({"type": 1})
        elif data["type"] == 2:
            if data['data']['name'] == "tag":
                if int(data['member']['user']['id']) in maintainers:
                    modal = {
                        "title": "New Tag",
                        "custom_id": "TAG_Modal",
                        "components": [{
                            "type": 1,
                            "components": [{
                                "type": 4,
                                "custom_id": "TAG_Modal_Name",
                                "style": 1,
                                "label": "Tag Name",
                                "max_length": 32
                            }]
                        },{
                            "type": 1,
                            "components": [{
                                "type": 4,
                                "custom_id": "TAG_Modal_Content",
                                "style": 1,
                                "label": "Tag Content",
                                "max_length": 1999
                            }]
                        }]
                    }
                    return jsonify({"type": 9, "data": modal})
                else:
                    return jsonify({"type": 4, "data": {"content": "You do not have permission to use this command.", "flags": 1 << 6}})
            elif data['data']['name'] == "ping":
                return jsonify({"type": 4, "data": {"content": "pong"}})
        elif data["type"] == 5:
            if data['data']['custom_id'] == "TAG_Modal":
                # TODO: add tag handler
                return f"tag_name: {data['data']['components'][0]['components'][0]['value']}, tag_value: {data['data']['components'][1]['components'][1]['value']}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)