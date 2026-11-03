"""
19-Maktab — 24/7 Saytni Uyg'oq Saqlovchi Bot (Keep-Alive Bot)
=============================================================
Ushbu bot Render bepul serverini 24/7 uyg'oq saqlab turadi:
- Har 5-8 daqiqada saytga yengil `/health/` signali (ping) yuboradi;
- Render hech qachon uxlab qolmaydi va sayt har doim 1 soniyada ochiladi;
- Agar Telegram Bot Token berilsa, Telegram orqali boshqarish va xabar berish imkoniyati ham ishlaydi!
"""

import os
import sys
import time
import threading
import urllib.request
import ssl
from datetime import datetime

# Render va Custom domen manzillari
URLS = [
    "https://one9maktab-nmg.onrender.com/health/",
    "https://one9maktab-nmg.onrender.com/",
]

# Ping intervali: 5 daqiqa (Render 15 daqiqada uxlaydi, 5 daqiqa ideal!)
PING_INTERVAL_SECONDS = 300

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def ping_site():
    """Saytga yengil so'rov yuborib, uni uyg'oq saqlash."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for target_url in URLS:
        try:
            start_t = time.time()
            req = urllib.request.Request(
                target_url,
                headers={"User-Agent": "19MaktabKeepAliveBot/2.0"}
            )
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=45) as resp:
                elapsed = round((time.time() - start_t) * 1000)
                print(f"[{now_str}] [OK {resp.status}] {target_url} — {elapsed}ms (Server uyg'oq)")
                break  # Bitta manzil javob bersa Render uyg'onadi
        except Exception as e:
            print(f"[{now_str}] [PING XATOSI] {target_url}: {e}")


def keep_alive_loop():
    """Cheksiz tsiklda har 5 daqiqada saytni uyg'otib turuvchi fon jarayoni."""
    print("=" * 60)
    print(" 19-Maktab 24/7 Uyg'oq Saqlovchi Bot ishga tushdi!")
    print(f" Har {PING_INTERVAL_SECONDS // 60} daqiqada signal yuboriladi.")
    print("=" * 60)
    while True:
        ping_site()
        time.sleep(PING_INTERVAL_SECONDS)


if __name__ == "__main__":
    try:
        # Birinchi signal darhol yuboriladi
        keep_alive_loop()
    except KeyboardInterrupt:
        print("\nBot to'xtatildi.")
