import logging
import html as _html

from telegram import Update
from telegram.ext import ContextTypes

from config import (
    BOT_NAME, UNIVERSITY, MAX_INPUT, DEBUG_MODE,
    SYSTEM_CHAT, SYSTEM_QUIZ_ASK, SYSTEM_QUIZ_EVAL,
)
from state import QuizState, get_state
from security import is_injection
from formatting import format_answer, send_html
from keyboards import main_kb, answer_kb, quiz_kb, confirm_kb
from ollama import ask
from texts import HELP_TEXT

log = logging.getLogger("studybot")


# ── Commands ────────────────────────────────────────────────────

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    get_state(context)
    name = _html.escape(update.effective_user.first_name)
    log.info(f"START | user={update.effective_user.id}")
    await update.message.reply_text(
        f"Hello, <b>{name}</b>! 👋\n\n"
        f"I'm <b>{BOT_NAME}</b> — your educational assistant at {_html.escape(UNIVERSITY)}.\n\n"
        "Ask me anything about math, programming, physics or databases.\n"
        "I remember our conversation — just chat naturally.\n\n"
        "To test your knowledge: <code>/quiz recursion</code>",
        parse_mode="HTML",
        reply_markup=main_kb(),
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML", reply_markup=main_kb())


async def cmd_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(context)
    await update.message.reply_text(state.stats.format(), parse_mode="HTML", reply_markup=main_kb())


async def cmd_clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(context)
    state.clear()
    log.info(f"CLEAR | user={update.effective_user.id}")
    await update.message.reply_text("🗑 Chat history cleared!", reply_markup=main_kb())


async def cmd_reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = get_state(context)
    state.full_reset()
    log.info(f"RESET | user={update.effective_user.id}")
    await update.message.reply_text("🔄 Full reset complete.", reply_markup=main_kb())


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/quiz <topic> — запускает quiz по теме."""
    state = get_state(context)
    topic = " ".join(context.args).strip() if context.args else ""

    if not topic:
        await update.message.reply_text(
            "Write the topic after the command.\n"
            "Example: <code>/quiz recursion</code>",
            parse_mode="HTML",
        )
        return

    await update.message.chat.send_action("typing")
    answer, elapsed, model = await ask(SYSTEM_QUIZ_ASK, [], f"Topic: {topic}")

    if model is None:
        state.stats.errors += 1
        await update.message.reply_text(format_answer(answer))
        return

    state.quiz              = QuizState()
    state.quiz.active       = True
    state.quiz.topic        = topic
    state.quiz.current_q    = answer
    state.quiz.question_num = 1
    state.stats.quiz_sessions += 1

    log.info(f"QUIZ_START | user={update.effective_user.id} | topic={topic} | model={model}")

    await send_html(
        update,
        f"<b>📝 Quiz: {_html.escape(topic)}</b>\n\n"
        f"<b>Question 1:</b>\n{format_answer(answer)}",
        reply_markup=quiz_kb(),
    )


# ── Inline buttons ──────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query  = update.callback_query
    await query.answer()
    state  = get_state(context)
    action = query.data

    if action == "ans_clear":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("Clear chat history?", reply_markup=confirm_kb())

    elif action == "ans_quiz":
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text(
            "Write the topic for a quiz:\n<code>/quiz your_topic</code>",
            parse_mode="HTML",
        )

    elif action == "stop_quiz":
        state.quiz = QuizState()
        await query.edit_message_reply_markup(reply_markup=None)
        await query.message.reply_text("🛑 Quiz stopped. Back to free chat!", reply_markup=main_kb())

    elif action == "stats":
        await query.edit_message_text(state.stats.format(), parse_mode="HTML", reply_markup=main_kb())

    elif action == "help":
        await query.edit_message_text(HELP_TEXT, parse_mode="HTML", reply_markup=main_kb())

    elif action == "confirm_clear":
        await query.edit_message_text("Clear chat history?", reply_markup=confirm_kb())

    elif action == "do_clear":
        state.clear()
        log.info(f"CLEAR | user={update.effective_user.id}")
        await query.edit_message_text("🗑 Chat history cleared!", reply_markup=main_kb())

    elif action == "cancel":
        await query.edit_message_text("Cancelled.", reply_markup=main_kb())


# ── Message handler ─────────────────────────────────────────────

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text.strip()
    uid       = update.effective_user.id

    if not user_text:
        return

    if len(user_text) > MAX_INPUT:
        await update.message.reply_text(
            f"⚠️ Message too long ({len(user_text)} chars). Max: {MAX_INPUT}."
        )
        return

    if is_injection(user_text):
        log.warning(f"INJECTION | user={uid} | text={user_text[:80]}")
        await update.message.reply_text("⚠️ This type of request is not supported.")
        return

    state = get_state(context)
    await update.message.chat.send_action("typing")

    # ── Quiz режим ───────────────────────────────────────────────
    if state.quiz.active:
        quiz = state.quiz
        context_msgs = [
            {"role": "assistant", "content": f"Question about «{quiz.topic}»: {quiz.current_q}"},
            {"role": "user",      "content": f"Student answer: {user_text}"},
        ]
        prompt = (
            f"Evaluate the answer and ask question #{quiz.question_num + 1} "
            f"about «{quiz.topic}»."
        )
        answer, elapsed, model = await ask(SYSTEM_QUIZ_EVAL, context_msgs, prompt)

        if model is not None:
            quiz.question_num += 1
            quiz.current_q    = answer

        state.stats.total_messages += 1
        if model is None:
            state.stats.errors += 1

        log.info(f"QUIZ_EVAL | user={uid} | q={quiz.question_num} | model={model} | {elapsed}s")

        await send_html(
            update,
            f"<b>Question {quiz.question_num}:</b>\n{format_answer(answer)}",
            reply_markup=quiz_kb(),
        )
        return

    # ── Обычный чат ──────────────────────────────────────────────
    answer, elapsed, model = await ask(SYSTEM_CHAT, state.history, user_text)

    state.history.append({"role": "user",      "content": user_text})
    state.history.append({"role": "assistant", "content": answer})
    if len(state.history) > MAX_INPUT * 2:
        state.history = state.history[-(MAX_INPUT * 2):]

    state.stats.total_messages += 1
    if model is None:
        state.stats.errors += 1

    log.info(f"MSG | user={uid} | model={model} | len={len(user_text)} | {elapsed}s")

    formatted = format_answer(answer)
    if DEBUG_MODE and elapsed:
        formatted += _html.escape(f"\n\n· {elapsed}s · {model or 'error'}")

    await send_html(update, formatted, reply_markup=answer_kb())
