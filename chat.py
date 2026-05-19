import requests  # Для HTTP-запросов к Ollama

# Константы — значения, которые не меняются
API_URL = "http://localhost:11434/api/generate"
MODEL = "gemma3:1b"

def send_message(prompt):
    """
    Отправляет сообщение в Ollama и возвращает ответ.
    Если что-то пошло не так — возвращает сообщение об ошибке.
    """
    # Формируем данные для запроса
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }

    try:
        # Отправляем POST-запрос, ждём не дольше 60 секунд
        response = requests.post(API_URL, json=payload, timeout=60)

        # Если сервер вернул ошибку (например 404 или 500) — вызываем исключение
        response.raise_for_status()

        # Читаем JSON-ответ и извлекаем текст
        return response.json()["response"]

    except requests.exceptions.ConnectionError:
        # Ollama не запущена или не отвечает
        return "❌ Ошибка: не могу подключиться к Ollama. Убедись, что она запущена (команда: ollama serve)"

    except requests.exceptions.Timeout:
        # Модель думает слишком долго
        return "⏳ Ошибка: модель не ответила за 60 секунд. Попробуй ещё раз."

    except KeyError:
        # В ответе нет поля "response" — неожиданный формат
        return "❌ Ошибка: неожиданный формат ответа от Ollama."

    except Exception as e:
        # Любая другая ошибка — выводим её описание
        return f"❌ Неизвестная ошибка: {e}"


def main():
    """Главная функция — запускает цикл чата."""
    print("=" * 50)
    print("  🤖 Чат-ассистент на базе Ollama")
    print(f"  Модель: {MODEL}")
    print("  Введи 'exit' или 'выход' чтобы завершить")
    print("=" * 50)
    print()

    # Бесконечный цикл — работает, пока пользователь не введёт exit
    while True:
        # Принимаем ввод; strip() убирает пробелы по краям
        user_input = input("Ты: ").strip()

        # Проверяем: не пустая ли строка
        if not user_input:
            print("(введи сообщение)\n")
            continue  # Возвращаемся в начало цикла

        # Проверяем команду выхода
        if user_input.lower() in ["exit", "выход", "quit"]:
            print("До свидания! 👋")
            break  # Выходим из цикла while

        # Отправляем сообщение и получаем ответ
        print("Ассистент: думаю...", end="\r")  # end="\r" — перезапишем эту строку
        answer = send_message(user_input)

        # Выводим ответ (пробел в конце затирает "думаю...")
        print(f"Ассистент: {answer}\n")


# Запускаем main() только если файл запущен напрямую (не импортирован)
if __name__ == "__main__":
    main()