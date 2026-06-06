import sqlite3
from datetime import datetime
import requests


def init_db():
    """Створює базу даних та таблицю, якщо вони ще не існують."""
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT NOT NULL,
            temperature TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


def get_khmelnytskyi_weather():
    """Отримує точну поточну температуру в Хмельницькому через стабільне Open-Meteo API."""
    # Координати Хмельницького: широта 49.42, довгота 26.98
    url = "https://api.open-meteo.com/v1/forecast?latitude=49.42&longitude=26.98&current=temperature_2m"

    try:
        # Робимо запит до погодного сервера
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Конвертуємо відповідь з формату JSON у звичайний словник Python
        data = response.json()

        # Дістаємо поточну температуру та одиницю виміру (градуси)
        current_temp = data["current"]["temperature_2m"]
        unit = data["current_units"]["temperature_2m"]

        # Повертаємо гарний рядок, наприклад: "+18.5°C" або "18.5°C"
        sign = "+" if current_temp > 0 else ""
        return f"{sign}{current_temp}{unit}"

    except Exception as e:
        return f"Помилка при отриманні API: {e}"


def save_to_db(temperature):
    """Записує дату, час та температуру в БД."""
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute(
        "INSERT INTO weather (datetime, temperature) VALUES (?, ?)",
        (current_time, temperature),
    )

    conn.commit()
    conn.close()
    print(f"Успішно збережено в БД. Час: {current_time} | Температура: {temperature}")


def check_saved_data():
    """Читає та виводить вміст бази даних у консоль для перевірки."""
    conn = sqlite3.connect("weather_data.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM weather")
    rows = cursor.fetchall()

    print("\n📊 --- ВМІСТ БАЗИ ДАНИХ SQLite ---")
    for row in rows:
        print(f"ID: {row[0]} | Дата/Час: {row[1]} | Температура: {row[2]}")
    print("----------------------------------")

    conn.close()


if __name__ == "__main__":
    print("Запуск програми...")

    # 1. Ініціалізуємо базу даних
    init_db()

    # 2. Запитуємо погоду через API
    print("Запит погоди для м. Хмельницький...")
    temp = get_khmelnytskyi_weather()

    print(f"Результат запиту: {temp}")

    # 3. Перевіряємо результат та записуємо
    if "Помилка" not in temp:
        save_to_db(temp)
        # 4. Виводимо всю таблицю на екран
        check_saved_data()
    else:
        print("Запис скасовано через помилку.")