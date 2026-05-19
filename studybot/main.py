import logging

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from config import (
    TELEGRAM_TOKEN, BOT_NAME, UNIVERSITY,
    MODEL_PRIMARY, MODEL_FALLBACK,
    MAX_HISTORY, RETRY_ATTEMPTS, DEBUG_MODE,
)
from handlers import (
    cmd_start, cmd_help, cmd_stats,
    cmd_clear, cmd_reset, cmd_quiz,
    button_handler, handle_message,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler("studybot.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("studybot")


def main():
    if not TELEGRAM_TOKEN:
        print("❌ Token not found! Add to .env: TELEGRAM_TOKEN=your_token")
        return

    w = 46
    print("╔" + "═" * w + "╗")
    print(f"║  📚  {BOT_NAME} v7.0 — {UNIVERSITY}".ljust(w + 1) + "║")
    print("╠" + "═" * w + "╣")
    print(f"║  Model    : {MODEL_PRIMARY}".ljust(w + 1) + "║")
    print(f"║  Fallback : {MODEL_FALLBACK}".ljust(w + 1) + "║")
    print(f"║  History  : {MAX_HISTORY} messages".ljust(w + 1) + "║")
    print(f"║  Retry    : {RETRY_ATTEMPTS} attempts".ljust(w + 1) + "║")
    print(f"║  Debug    : {'ON' if DEBUG_MODE else 'OFF'}".ljust(w + 1) + "║")
    print(f"║  Log      : studybot.log".ljust(w + 1) + "║")
    print(f"║  Stop     : Ctrl+C".ljust(w + 1) + "║")
    print("╚" + "═" * w + "╝\n")

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help",  cmd_help))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("clear", cmd_clear))
    app.add_handler(CommandHandler("reset", cmd_reset))
    app.add_handler(CommandHandler("quiz",  cmd_quiz))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    log.info(f"{BOT_NAME} v7.0 started | model={MODEL_PRIMARY}")
    app.run_polling()


if __name__ == "__main__":
    main()
