import html as _html

from config import BOT_NAME, UNIVERSITY

HELP_TEXT = (
    f"<b>{BOT_NAME}</b> — Educational Assistant | {_html.escape(UNIVERSITY)}\n\n"
    "Just ask me anything:\n"
    "📐 Math — problems, formulas, proofs\n"
    "💻 Programming — Python, C++, SQL\n"
    "⚡ Physics — problems, concepts, laws\n"
    "🗄 Databases — SQL, queries, design\n"
    "🔢 Algorithms — sorting, complexity\n\n"
    "I remember our conversation context.\n\n"
    "<b>Special mode:</b>\n"
    "/quiz <i>topic</i> — start a knowledge quiz on any topic\n\n"
    "<b>Commands:</b>\n"
    "/clear — clear chat history\n"
    "/reset — full reset (history + stats)\n"
    "/stats — usage statistics\n"
    "/help  — this message"
)
