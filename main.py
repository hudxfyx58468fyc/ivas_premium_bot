import asyncio
import websockets
import json
import os
import requests

# Load from environment
TELEGRAM_BOT_TOKEN = os.environ.get("BOT_TOKEN")
TELEGRAM_CHANNEL_ID = os.environ.get("CHANNEL_ID")
IVASMS_WS_URL = os.environ.get("IVASMS_WS_URL")
IVASMS_AUTH_TOKEN = os.environ.get("IVASMS_AUTH_TOKEN")

async def connect():
    while True:
        try:
            async with websockets.connect(IVASMS_WS_URL) as ws:
                print("✅ WebSocket connected")

                await ws.send("40/livesms")
                await ws.send(f'42["auth","{IVASMS_AUTH_TOKEN}"]')
                print("🔐 Sent auth token")

                while True:
                    msg = await ws.recv()
                    if "42" in msg and "sms" in msg:
                        payload = json.loads(msg[2:])
                        otp_data = payload[1]
                        otp = otp_data.get("otp")
                        number = otp_data.get("number")

                        text = f"📩 OTP Received\nNumber: {number}\nCode: {otp}"
                        requests.get(
                            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
                            params={"chat_id": TELEGRAM_CHANNEL_ID, "text": text}
                        )
                        print("🚀 OTP sent to Telegram")

        except Exception as e:
            print(f"❌ Error: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

asyncio.run(connect())
