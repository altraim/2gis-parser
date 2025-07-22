import asyncio
import os
from dotenv import load_dotenv
from parser import parse_reviews
from db import init_db, get_existing_ids, save_reviews
from notifier import send_to_telegram

load_dotenv()

async def main():
    urls = os.getenv("BRANCH_URLS", "").split(",")
    if not urls:
        print("❌ Нет URL филиалов")
        return

    init_db()
    known_ids = get_existing_ids()
    all_new = []

    # Асинхронный парсинг всех филиалов
    tasks = [parse_reviews(url) for url in urls]
    results = await asyncio.gather(*tasks)
    
    # Обработка результатов
    for reviews in results:
        new_reviews = [r for r in reviews if r["id"] not in known_ids]
        all_new.extend(new_reviews)

        # Отправка уведомлений
        for r in new_reviews:
            msg = (
                f"👤 {r['author']} | {r['rating']}⭐\n"
                f"🗓 {r['date']}\n"
                f"💬 {r['text']}\n"
                f"📍 Филиал: {r['branch_url']}\n"
            )
            await send_to_telegram(msg)

    save_reviews(all_new)
    print(f"\n✅ Найдено новых отзывов: {len(all_new)}")

if __name__ == "__main__":
    asyncio.run(main())