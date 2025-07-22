import asyncio
from playwright.async_api import async_playwright
from db import get_existing_ids
import hashlib
from urllib.parse import urlparse, parse_qs
from utils.date_converter import convert_date_word

async def parse_single_review(url):
    """Парсит данные конкретного отзыва по ссылке"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        try:
            await page.goto(url, timeout=60000)
            
            # Ждем появления основного контейнера отзыва
            await page.wait_for_selector('//*[@id="root"]/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div')
            one_review = page.locator('//*[@id="root"]/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div/div/div[2]/div/div[1]/div/div/div/div/div')
            
            # Получаем URL филиала (обрезаем после /review/)
            branch_url = '/'.join(url.split('/')[:6])
            # Получаем элементы с явным ожиданием
            style_elements = await one_review.locator('//div[3]/div[1]/div/div[1]/span').all()
            date_elements = await one_review.locator('//div[1]/div/div[1]/div[2]/div').all()
            
            # Извлекаем данные с проверкой наличия элементов
            author = await one_review.locator('//div[1]/div/div[1]/div[2]/span/span[1]/span').get_attribute('title') or "Аноним"
            style = await style_elements[0].get_attribute('style') if style_elements else ""
            rating = int(style[-5]) if style else 0
            
            text = await one_review.locator('//div[3]/div[2]/a').inner_text()
            
            date_raw = await date_elements[0].inner_text() if date_elements else ""
            date = convert_date_word(date_raw)
            review_id = hashlib.md5(f"{author}{text}{date}".encode()).hexdigest()
            
            review_data = {
                "id": review_id,
                "author": author,
                "text": text,
                "rating": rating,
                "date": date,
                "branch_url": branch_url
            }
            
            return review_data
            
        except Exception as e:
            print(f"Ошибка при парсинге отзыва: {e}")
            return None
        finally:
            await browser.close()

async def check_review_in_db(review_url):
    """Проверяет наличие отзыва в базе данных"""
    try:
        # Парсим данные отзыва
        review_data = await parse_single_review(review_url)
        if not review_data:
            return False
            
        print(f"\nДанные отзыва:")
        print(f"Филиал: {review_data['branch_url']}")
        print(f"Автор: {review_data['author']}")
        print(f"Рейтинг: {'★' * review_data['rating']}{'☆' * (5 - review_data['rating'])}")
        print(f"Дата: {review_data['date']}")
        print(f"Текст: {review_data['text']}")
        
        # Проверяем в базе данных
        existing_ids = get_existing_ids()
        if review_data['id'] in existing_ids:
            print(f"\n✅ Отзыв найден в базе (ID: {review_data['id']})")
            return True
        else:
            print(f"\n❌ Отзыв отсутствует в базе (ID: {review_data['id']})")
            return False
            
    except Exception as e:
        print(f"\nОшибка при проверке отзыва: {e}")
        return False

if __name__ == "__main__":
    print("=== Проверка отзыва в базе данных ===")
    
    # Запрашиваем ссылку у пользователя
    while True:
        review_url = input("\nВведите ссылку на отзыв (или 'exit' для выхода): ").strip()
        
        if review_url.lower() in ('exit', 'выход'):
            print("Завершение работы...")
            break
        
        if not review_url.startswith('https://2gis.ru'):
            print("❌ Ошибка: Ссылка должна начинаться с 'https://2gis.ru'")
            continue
        
        print(f"\nПроверяем отзыв: {review_url}")
        
        try:
            result = asyncio.run(check_review_in_db(review_url))
            print(f"\nИтоговый результат: {'✅ Найден в базе' if result else '❌ Не найден в базе'}")
        except Exception as e:
            print(f"\n⚠ Произошла ошибка при проверке: {e}")
        
        print("\n" + "="*50)