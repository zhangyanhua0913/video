#coding=utf-8

'''
requires Python 3.6 or later
pip install requests
'''
import base64
import json
import uuid
import requests
import traceback

# 填写平台申请的appid, access_token以及cluster
appid = "9847999155"
# access_token= "WkRrd05ETm1NekV5TkRFMk5EaGtNMkpoTnpnd09UUmtNVE5pTnpCaE1tSQ=="
access_token= "nAblyxkQTcVaeBu4M0rKaphRuwkdlbOV"
cluster = "volcano_tts"

voice_type = "BV700_V2_streaming"
host = "openspeech.bytedance.com"
api_url = f"https://{host}/api/v1/tts"

header = {"Authorization": f"Bearer;{access_token}"}

request_json = {
    "app": {
        "appid": appid,
        "token": "access_token",
        "cluster": cluster
    },
    "user": {
        "uid": "388808087185088"
    },
    "audio": {
        "voice_type": voice_type,
        "encoding": "mp3",
        "speed_ratio": 1.0,
        "volume_ratio": 1.0,
        "pitch_ratio": 1.0,
    },
    "request": {
        "reqid": str(uuid.uuid4()),
        "text": "字节跳动语音合成",
        "text_type": "plain",
        "operation": "query",
        "with_frontend": 1,
        "frontend_type": "unitTson"

    }
}

if __name__ == '__main__':
    try:
        with requests.Session() as session:
            # Force direct connection and ignore system proxy env vars.
            session.trust_env = False
            resp = session.post(
                api_url,
                json=request_json,
                headers={**header, "Content-Type": "application/json; charset=utf-8"},
                timeout=30,
            )
        body = resp.json()
        print(f"status: {resp.status_code}")
        print(f"resp body: \n{body}")
        if "data" in body:
            data = body["data"]
            with open("test_submit.mp3", "wb") as file_to_save:
                file_to_save.write(base64.b64decode(data))
            print("saved: test_submit.mp3")
    except Exception as e:
        print(f"request failed: {e}")
        traceback.print_exc()
