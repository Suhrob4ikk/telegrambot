from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("📊 Stats",  callback_data="stats"),
        InlineKeyboardButton("🗑 Clear",  callback_data="confirm_clear"),
        InlineKeyboardButton("ℹ️ Help",   callback_data="help"),
    ]])


def answer_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🗑 Clear chat", callback_data="ans_clear"),
        InlineKeyboardButton("📝 Start Quiz", callback_data="ans_quiz"),
    ]])


def quiz_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🛑 Stop Quiz", callback_data="stop_quiz"),
    ]])


def confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Yes, clear", callback_data="do_clear"),
        InlineKeyboardButton("❌ Cancel",     callback_data="cancel"),
    ]])
