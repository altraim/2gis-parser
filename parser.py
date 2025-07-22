from playwright.async_api import async_playwright
from utils.date_converter import convert_date_word
import hashlib

async def parse_reviews(url):
    async with async_playwright() as p:
        browser = await p.webkit.launch(headless=True)
        page = await browser.new_page()
        reviews_list = []

        try:
            # Переход на страницу
            await page.goto(url)

            # Получаем количество отзывов
            review_count_html = await page.locator(
                '//*[@id="root"]/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div/div[2]/div[1]/div[2]/div[3]/div/div[1]/div[3]/h2/a/span'
            ).inner_text()
            review_count = int(review_count_html.replace(" ", "").strip())
            print(f"🔢 Всего отзывов: {review_count}")
            
            await page.locator(
                '//*[@id="root"]/div/div/div[3]/div[1]/div[3]'
            ).click()
            
            # Открываем вкладку "Отзывы"
            await page.locator(
                '//*[@id="root"]/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div/div[2]/div[1]/div[2]/div[3]/div/div[1]/div[3]/h2/a'
            ).click()

            # Скроллим/загружаем до конца
            while True:
                try:
                    load_more = page.get_by_text("Загрузить ещё")
                    await load_more.scroll_into_view_if_needed()
                    await load_more.click()
                except:
                    print("ℹ️ Нет кнопки 'Загрузить ещё'")
                    break

            # Получаем все элементы отзывов
            elements = await page.locator(
                '//*[@id="root"]/div/div/div[1]/div[1]/div[3]/div[2]/div/div/div/div/div[2]/div[2]/div/div[1]/div/div/div/div/div[2]/div[2]/div/div'
            ).all()
            
            extra_elem = await elements[2].inner_text()
            
            if "Люди говорят" in extra_elem:
                reviews_raw = elements[5:]
            else:
                reviews_raw = elements[4:]
                
            print(f"✅ Загружено отзывов: {len(reviews_raw)}")

            for one_review in reviews_raw:
                try:
                    # Получаем все элементы перед обращением по индексу
                    style_elements = await one_review.locator('//div[3]/div[1]/div/div[1]/span').all()
                    date_elements = await one_review.locator('//div[1]/div/div[1]/div[2]/div').all()
                    
                    author = await one_review.locator('//div[1]/div/div[1]/div[2]/span/span[1]/span').get_attribute('title') or "Аноним"
                    style = await style_elements[0].get_attribute('style') if style_elements else ""
                    rating = int(style[7]) if style else 0
                    text = await one_review.locator('//div[3]/div[2]/a').inner_text()
                    date_raw = await date_elements[0].inner_text() if date_elements else ""
                    date = convert_date_word(date_raw)

                    review_id = hashlib.md5(f"{author}{text}{date}".encode()).hexdigest()

                    reviews_list.append({
                        "id": review_id,
                        "author": author,
                        "text": text,
                        "rating": rating,
                        "date": date,
                        "branch_url": url
                    })

                except Exception as e:
                    print(f"[!] Ошибка при разборе одного отзыва: {e}")

            return reviews_list

        except Exception as e:
            print(f"❌ Ошибка при парсинге страницы: {e}")
            return []

        finally:
            await browser.close()