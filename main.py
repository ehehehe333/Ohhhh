import asyncio
import httpx
import time
import random
from fastapi import FastAPI
import uvicorn
import os

LOGIN_URL = "https://sso.garena.com/api/login"
PRELOGIN_URL = "https://sso.garena.com/api/prelogin"

ACCOUNT = "Onlylove-lavi"
PASSWORD = "a6af2aa1bf8180e24dbcebe5b59a03fc"
APP_ID = "10100"
REDIRECT_URI = "https://account.garena.com/"
PORT = int(os.environ.get("PORT", 10000))  # Render tự set PORT

headers = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36",
    "Referer": f"https://sso.garena.com/universal/login?app_id={APP_ID}&redirect_uri={REDIRECT_URI}&locale=vi-VN"
}

def gen_id():
    return str(int(time.time() * 1000)) + str(random.randint(100, 999))

async def send_login(client: httpx.AsyncClient):
    prelogin_params = {
        "app_id": APP_ID,
        "account": ACCOUNT,
        "format": "json",
        "id": gen_id()
    }

    login_params = {
        "app_id": APP_ID,
        "account": ACCOUNT,
        "password": PASSWORD,
        "redirect_uri": REDIRECT_URI,
        "format": "json",
        "id": gen_id()
    }

    try:
        pre = await client.get(PRELOGIN_URL, headers=headers, params=prelogin_params)
        print(f"[Prelogin] {pre.status_code}")
        await asyncio.sleep(random.uniform(0.05, 0.2))
        res = await client.get(LOGIN_URL, headers=headers, params=login_params)
        print(f"[Login] {res.status_code} {res.text}")
    except Exception as e:
        print(f"[LỖI] {e}")

async def spam_loop():
    async with httpx.AsyncClient(http2=True, timeout=10) as client:
        while True:
            tasks = [send_login(client) for _ in range(10)]
            await asyncio.gather(*tasks)
            await asyncio.sleep(0.5)

app = FastAPI()

@app.get("/")
async def root():
    return {"msg": "I’m awake 😎"}

async def self_ping():
    async with httpx.AsyncClient() as client:
        while True:
            try:
                url = f"http://localhost:{PORT}/"
                await client.get(url)
                print(f"[Ping] -> {url}")
            except Exception as e:
                print(f"[PING ERROR] {e}")
            await asyncio.sleep(280)  # ~4.6 phút

@app.on_event("startup")
async def on_start():
    asyncio.create_task(spam_loop())
    asyncio.create_task(self_ping())

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=PORT)
