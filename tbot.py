"""
DonishAI — Учебный ассистент для студентов МГУ Душанбе
Телеграм-бот на основе локальной нейросети через Ollama

Запуск: python main.py
Требования: pip install python-telegram-bot httpx python-dotenv
"""

import os
import re
import logging
import html
from dataclasses import dataclass, field

import httpx
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    filters, ContextTypes,
)

# ── Логирование ──────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    handlers=[
        logging.FileHandler("donishai.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)

# ── Конфигурация ─────────────────────────────────────────────
load_dotenv(dotenv_path=".env.donish")
TOKEN       = os.getenv("TELEGRAM_TOKEN")
OLLAMA_URL  = "http://localhost:11434/api/chat"
MODEL       = "qwen2.5:3b"
MAX_HISTORY = 20    # сообщений в памяти
MAX_INPUT   = 2000  # символов от пользователя
TG_LIMIT    = 4096  # лимит Telegram

# ── Текст помощи ─────────────────────────────────────────────
HELP_TEXT = (
    "<b>DonishAI</b> — Учебный ассистент МГУ Душанбе\n\n"
    "📐 Математика — задачи, формулы, доказательства\n"
    "💻 Программирование — Python, C++, SQL\n"
    "⚡ Физика — задачи, законы, концепции\n"
    "🗄 Базы данных — SQL, запросы, проектирование\n\n"
    "<b>Команды:</b>\n"
    "/clear — очистить историю\n"
    "/help  — эта справка"
)

# ── Системный промпт ─────────────────────────────────────────
SYSTEM_PROMPT = """Ты DonishAI — учебный ассистент для студентов МГУ Душанбе.

Темы: математика, программирование (Python, C++), физика, базы данных, алгоритмы.

Правила:
1. Отвечай ТОЛЬКО если уверен. Если не знаешь — скажи: "Не знаю, проверь в учебнике."
2. НЕ выдумывай факты, формулы, определения.
3. Если вопрос не по учёбе — вежливо откажи.
4. Для задач: Дано → Решение → Ответ.
5. Для кода: укажи ошибку, объясни почему, покажи исправленный вариант.
6. Отвечай на том языке, на котором задан вопрос.
7. Никакого лишнего текста — только по делу."""

# ── Состояние пользователя ───────────────────────────────────
@dataclass
class UserState:
    history:    list = field(default_factory=list)
    processing: bool = False

def get_state(context: ContextTypes.DEFAULT_TYPE) -> UserState:
    if "state" not in context.user_data:
        context.user_data["state"] = UserState()
    return context.user_data["state"]

# ── Ollama запрос ────────────────────────────────────────────
async def ask_ollama(client: httpx.AsyncClient, history: list, user_text: str) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-(MAX_HISTORY * 2):]
    messages.append({"role": "user", "content": user_text})

    payload = {
        "model": MODEL,
        "messages": messages,
        "stream": False,
        "options": {"num_predict": 600, "temperature": 0.5},
    }
    try:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
        return r.json()["message"]["content"].strip()
    except httpx.ConnectError:
        return "❌ Ollama не запущена. Выполни: <code>ollama serve</code>"
    except httpx.TimeoutException:
        return "⏳ Модель не ответила. Попробуй сформулировать вопрос короче."
    except Exception as e:
        log.error(f"Ollama error: {e}")
        return "❌ Ошибка соединения. Попробуй позже."

# ── Форматирование ───────────────────────────────────────────
def format_response(text: str) -> str:
    """Конвертирует Markdown в Telegram HTML."""
    if text.count("```") % 2 != 0:
        text += "\n```"
    parts, last = [], 0
    for m in re.finditer(r'```(\w*)\n?(.*?)```', text, re.DOTALL):
        parts.append(_md_inline(text[last:m.start()]))
        lang = m.group(1).strip()
        code = html.escape(m.group(2).strip())
        tag  = f' class="language-{lang}"' if lang else ""
        parts.append(f"<pre><code{tag}>{code}</code></pre>")
        last = m.end()
    parts.append(_md_inline(text[last:]))
    return "".join(parts)

def _md_inline(text: str) -> str:
    parts, last = [], 0
    for m in re.finditer(r'`([^`]+)`', text):
        parts.append(html.escape(text[last:m.start()]))
        parts.append(f"<code>{html.escape(m.group(1))}</code>")
        last = m.end()
    parts.append(html.escape(text[last:]))
    text = "".join(parts)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text, flags=re.DOTALL)
    return text

async def send(update: Update, text: str, markup=None):
    while len(text) > TG_LIMIT:
        i = text.rfind("\n\n", 0, TG_LIMIT)
        if i == -1:
            i = text.rfind("\n", 0, TG_LIMIT)
        if i == -1:
            i = TG_LIMIT
        await update.message.reply_text(text[:i], parse_mode="HTML")
        text = text[i:].lstrip()
    if text:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=markup)
        
# ── Клавиатуры ───────────────────────────────────────────────
def kb_main() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑 Очистить историю", callback_data="clear"),
        InlineKeyboardButton("ℹ️ Помощь",            callback_data="help"),
    ]])

def kb_confirm() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Да, очистить", callback_data="do_clear"),
        InlineKeyboardButton("❌ Отмена",       callback_data="cancel"),
    ]])

# ── Команды ──────────────────────────────────────────────────
async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = html.escape(update.effective_user.first_name)
    await update.message.reply_text(
        f"Привет, <b>{name}</b>! 👋\n\n"
        f"Я <b>DonishAI</b> — учебный ассистент МГУ Душанбе.\n\n"
        f"Задавай вопросы по математике, программированию, физике или базам данных.\n",
        parse_mode="HTML",
        reply_markup=kb_main(),
    )

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML", reply_markup=kb_main())

async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Очистить историю чата?", reply_markup=kb_confirm())

# ── Кнопки ───────────────────────────────────────────────────
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    state  = get_state(context)
    action = query.data

    if action == "clear":
        await query.edit_message_text("Очистить историю чата?", reply_markup=kb_confirm())

    elif action == "do_clear":
        state.history = []
        await query.edit_message_text("🗑 История очищена.", reply_markup=kb_main())

    elif action == "cancel":
        await query.edit_message_text("Отменено.", reply_markup=kb_main())

    elif action == "help":
        await query.edit_message_text(HELP_TEXT, parse_mode="HTML", reply_markup=kb_main())

# ── Обработка сообщений ──────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    if not user_text:
        return

    state = get_state(context)
    uid   = update.effective_user.id

    if len(user_text) > MAX_INPUT:
        await update.message.reply_text(
            f"⚠️ Сообщение слишком длинное ({len(user_text)} симв.). Максимум: {MAX_INPUT}."
        )
        return

    if state.processing:
        await update.message.reply_text("⏳ Подожди, обрабатываю предыдущий запрос.")
        return

    state.processing = True
    try:
        await update.effective_chat.send_action("typing")
        client = context.bot_data["http_client"]
        answer = await ask_ollama(client, state.history, user_text)

        state.history.append({"role": "user",      "content": user_text})
        state.history.append({"role": "assistant", "content": answer})
        if len(state.history) > MAX_HISTORY * 2:
            state.history = state.history[-(MAX_HISTORY * 2):]

        log.info(f"MSG | user={uid} | len={len(user_text)}")
        await send(update, format_response(answer))
    finally:
        state.processing = False

# ── HTTP клиент ──────────────────────────────────────────────
async def on_startup(app):
    app.bot_data["http_client"] = httpx.AsyncClient(
        timeout=httpx.Timeout(120.0, connect=5.0)
    )

async def on_shutdown(app):
    await app.bot_data["http_client"].aclose()

# ── Запуск ───────────────────────────────────────────────────
def main():
    if not TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN не задан в .env.donish")

    print("╔══════════════════════════════════════╗")
    print("║  📚  DonishAI — МГУ Душанбе          ║")
    print(f"║  Модель : {MODEL:<27}║")
    print("║  Стоп   : Ctrl+C                     ║")
    print("╚══════════════════════════════════════╝\n")

    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .post_init(on_startup)
        .post_shutdown(on_shutdown)
        .build()
    )

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info(f"DonishAI started | model={MODEL}")
    app.run_polling()


if __name__ == "__main__":
    main()