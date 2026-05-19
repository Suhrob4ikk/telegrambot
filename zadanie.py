"""
DonishAI — Учебный ассистент для студентов МГУ Душанбе
Работает через Ollama (локальная нейросеть qwen2.5:3b)

Запуск: streamlit run main.py
Требования: pip install streamlit ollama
"""

import streamlit as st
import ollama

# ── Настройки ────────────────────────────────────────────────
MODEL = "qwen2.5:3b"

# Низкая температура = меньше "творчества", меньше галлюцинаций
TEMPERATURE = 0.1

SYSTEM_PROMPT = """Ты DonishAI — учебный ассистент для студентов МГУ Душанбе.
Темы: математика, программирование (Python, C++), физика, базы данных, алгоритмы.

━━━ САМОЕ ВАЖНОЕ ━━━
ПЕРЕД ответом выполни внутреннюю проверку:
1. Есть ли в ответе термины, которых ты не уверен? → убери их.
2. Совпадает ли код с тем, что ты написал в объяснении? → проверь.
3. Соответствует ли формула стандартному определению? → проверь.
Если не уверен — напиши «Не знаю» или «Уточни вопрос».

━━━ ЗАПРЕЩЕНО ━━━
- Вводить новые обозначения вместо стандартных (например, I = V/G вместо I = V/R — ОШИБКА).
- Использовать несуществующие термины («конечный закон», «статическая динамическая структура» — ОШИБКА).
- Заменять формулы метафорами или аналогиями.
- Описывать в объяснении то, чего нет в коде.
- Давать неполный код с пометкой «и так далее».

━━━ ФИЗИКА И МАТЕМАТИКА ━━━
Формат: Дано → Найти → Решение (шаг за шагом) → Ответ
- Только стандартные формулы из учебников. Никаких авторских интерпретаций.
- Пример правильно: I = V / R (закон Ома). Не менять обозначения.
- Каждый шаг — одно действие + единица измерения.

━━━ КОД ━━━
Формат при исправлении: [Ошибка] → [Причина] → [Полный исправленный код]
Формат при написании: [Полный рабочий код] → [Объяснение строк]
- Код обязан обрабатывать ВСЕ случаи, упомянутые в объяснении.
- Мысленно выполни код на 2–3 примерах перед ответом. Если результат неверный — перепиши.
- re.sub(r'[^\w\s]', '', s) НЕ удаляет пробелы — это ошибка для задачи палиндром.

━━━ ТЕОРИЯ ━━━
- Одно точное определение. Без воды.
- std::array: фиксированный размер, ВСЕГДА на стеке. Размер задаётся на этапе компиляции.
- std::vector: динамический, данные на куче (heap). Размер — в runtime. Есть capacity и size.
- Не смешивать эти понятия.

━━━ СТИЛЬ ━━━
- Без вступлений («Конечно!», «Отличный вопрос!»).
- Язык ответа = язык вопроса (русский или английский)."""


# ── Стриминг с явным сбором ответа ───────────────────────────
def stream_and_collect(messages):
    """Стримит ответ и параллельно собирает полную строку."""
    collected = []

    def _gen():
        stream = ollama.chat(
            model=MODEL,
            messages=messages,
            stream=True,
            options={"temperature": TEMPERATURE},
        )
        for chunk in stream:
            text = chunk["message"]["content"]
            collected.append(text)
            yield text

    return _gen(), collected


# ── Интерфейс ─────────────────────────────────────────────────
def main():
    st.set_page_config(page_title="DonishAI", page_icon="📚")
    st.title("📚 DonishAI — Учебный ассистент")
    st.caption(f"МГУ Душанбе · Модель: {MODEL} · temp={TEMPERATURE}")

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # Сайдбар
    with st.sidebar:
        st.header("Настройки")
        msg_count = len(st.session_state.messages) - 1
        st.caption(f"Сообщений в диалоге: {msg_count}")
        if st.button("🗑 Очистить историю", use_container_width=True):
            st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            st.rerun()

    # История
    for msg in st.session_state.messages[1:]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Ввод
    user_input = st.chat_input("Задай вопрос по учёбе...")
    if not user_input:
        return

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            gen, collected = stream_and_collect(st.session_state.messages)
            st.write_stream(gen)
            full_response = "".join(collected)
            if full_response.strip():
                st.session_state.messages.append({"role": "assistant", "content": full_response})
            else:
                st.warning("Модель вернула пустой ответ. Попробуй переформулировать вопрос.")
        except ollama.ResponseError as e:
            st.error(f"Ошибка модели: {e}. Проверь, что модель загружена (`ollama pull {MODEL}`).")
        except Exception:
            st.error("Не удалось подключиться к Ollama. Убедись, что сервис запущен (`ollama serve`).")


if __name__ == "__main__":
    main()
