import csv
import requests
from bs4 import BeautifulSoup
import time

def fetch_website_text(url):
    # Загружает HTML-страницу по URL и извлекает из неё текст.
    try:
        # Заголовки, чтобы сайт думал, что это обычный браузер
        headers = {"User-Agent": "Mozilla/5.0"}
        # Запрос страницы
        r = requests.get(url, headers=headers, timeout=10)

        # Парсинг HTML
        soup = BeautifulSoup(r.text, "html.parser")

        # Извлекаем весь читаемый текст со страницы
        texts = soup.stripped_strings

        # Объединяем текст в одну строку
        combined = " ".join(texts)

        # Ограничиваем длину текста (чтобы не перегружать обработку)
        return combined[:3000]

    except Exception as e:
        # В случае ошибки возвращаем пустую строку
        return ""


def simple_extract(text):
    """
    Простой метод извлечения "персонализации" из текста:
    ищет предложения с ключевыми словами.
    """
    # Ключевые слова для поиска релевантной информации
    keywords = ["founded", "year", "company", "platform", "service", "client", "leader"]

    # Разбиваем текст на предложения
    sentences = text.split(".")

    # Ищем первое подходящее предложение
    for s in sentences:
        for k in keywords:
            if k in s.lower():
                return s.strip()[:200]

    # Если ничего не найдено — возвращаем обрезанный текст
    return text[:200]


def process_csv(input_file, output_file):
    """
    Обрабатывает CSV файл:
    - читает компании
    - парсит сайт
    - извлекает текст
    - добавляет поле Personalization
    - сохраняет результат в новый файл
    """
    with open(input_file, newline='', encoding='utf-8') as infile, \
            open(output_file, 'w', newline='', encoding='utf-8') as outfile:

        # Чтение входного CSV
        reader = csv.DictReader(infile)

        # Добавляем новое поле в выходной файл
        fieldnames = reader.fieldnames + ["Personalization"]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)

        # Записываем заголовки
        writer.writeheader()

        # Обрабатываем каждую строку
        for row in reader:
            # Получаем сайт компании (поддержка разных названий колонок)
            website = row.get("Сайт") or row.get("Website") or ""

            # Загружаем текст с сайта
            text = fetch_website_text(website)

            # Извлекаем полезную информацию
            if text:
                personalization = simple_extract(text)
            else:
                personalization = "No data found"

            # Добавляем результат в строку
            row["Personalization"] = personalization

            # Записываем строку в выходной файл
            writer.writerow(row)

            # Лог обработки
            print(f"Processed: {row.get('Компания', 'Unknown')}")

            # Пауза, чтобы не перегружать сайты
            time.sleep(1)


if __name__ == "__main__":
    input_file = "input.csv"
    output_file = "output.csv"

    # Запуск обработки
    process_csv(input_file, output_file)
    print("Done!")
