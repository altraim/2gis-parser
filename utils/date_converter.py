from datetime import datetime, timedelta

def convert_date_word(text):
    # Словарь месяцев
    months = {
        1: 'января', 2: 'февраля', 3: 'марта',
        4: 'апреля', 5: 'мая', 6: 'июня',
        7: 'июля', 8: 'августа', 9: 'сентября',
        10: 'октября', 11: 'ноября', 12: 'декабря'
    }
    
    today = datetime.now()
    redacted = ", отредактирован" if "отредактирован" in text.lower() else ""
    
    if "сегодня" in text.lower():
        day = today.day
        month = months[today.month]
        year = today.year
    elif "вчера" in text.lower():
        yesterday = today - timedelta(days=1)
        day = yesterday.day
        month = months[yesterday.month]
        year = yesterday.year
    else:
        return text
    
    return f"{day} {month} {year}{redacted}"
