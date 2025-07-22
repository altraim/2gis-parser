import aiohttp
import os

async def send_to_telegram(message):
    """Асинхронная отправка сообщения в Telegram"""
    token = os.getenv("TG_BOT_TOKEN")
    chat_id = os.getenv("TG_CHAT_ID")
    
    if not token or not chat_id:
        print("❌ Не заданы настройки Telegram")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    print(f"❌ Ошибка отправки: {await response.text()}")
    except Exception as e:
        print(f"❌ Ошибка соединения с Telegram: {e}")