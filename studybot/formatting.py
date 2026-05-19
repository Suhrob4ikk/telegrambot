import re
import html as _html

from telegram import Update

from config import TELEGRAM_LIMIT


def strip_latex(text: str) -> str:
    """Принудительно конвертирует LaTeX → Unicode."""
    text = re.sub(r'\\\[|\\\]|\\\(|\\\)', '', text)
    text = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', r'(\1)/(\2)', text)
    text = re.sub(r'\\sqrt\{([^}]+)\}', r'√(\1)', text)
    text = re.sub(r'\\sqrt\s', '√', text)

    sup_map = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
    def sup(m): return m.group(1).translate(sup_map)
    text = re.sub(r'\^\{([0-9]+)\}', sup, text)
    text = re.sub(r'\^([0-9])',       sup, text)
    text = re.sub(r'_\{([^}]+)\}', r'_\1', text)

    table = {
        r'\alpha':'α', r'\beta':'β', r'\gamma':'γ', r'\delta':'δ',
        r'\epsilon':'ε', r'\theta':'θ', r'\lambda':'λ', r'\mu':'μ',
        r'\pi':'π', r'\sigma':'σ', r'\phi':'φ', r'\omega':'ω',
        r'\Sigma':'Σ', r'\Delta':'Δ', r'\Omega':'Ω',
        r'\cdot':'·', r'\times':'×', r'\div':'÷',
        r'\leq':'≤', r'\geq':'≥', r'\neq':'≠', r'\approx':'≈',
        r'\infty':'∞', r'\pm':'±', r'\in':'∈', r'\notin':'∉',
        r'\sum':'Σ', r'\int':'∫', r'\partial':'∂',
        r'\to':'→', r'\Rightarrow':'⟹', r'\Leftrightarrow':'⟺',
    }
    for k, v in table.items():
        text = text.replace(k, v)

    text = re.sub(r'\\[a-zA-Z]+\*?', '', text)
    text = re.sub(r'(?<!\w)\{|\}(?!\w)', '', text)
    return text


def _inline_to_html(text: str) -> str:
    parts, last = [], 0
    for m in re.finditer(r'`([^`]+)`', text):
        parts.append(_html.escape(text[last:m.start()]))
        parts.append(f"<code>{_html.escape(m.group(1))}</code>")
        last = m.end()
    parts.append(_html.escape(text[last:]))
    text = "".join(parts)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'__(.+?)__',     r'<b>\1</b>', text, flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*',     r'<i>\1</i>', text, flags=re.DOTALL)
    text = re.sub(r'_([^_\n]+)_',   r'<i>\1</i>', text)
    return text


def md_to_html(text: str) -> str:
    result, last = [], 0
    for m in re.finditer(r'```(\w*)\n?(.*?)```', text, re.DOTALL):
        result.append(_inline_to_html(text[last:m.start()]))
        lang = m.group(1).strip()
        code = _html.escape(m.group(2).strip())
        tag  = f' class="language-{lang}"' if lang else ""
        result.append(f"<pre><code{tag}>{code}</code></pre>")
        last = m.end()
    result.append(_inline_to_html(text[last:]))
    return "".join(result)


def format_answer(text: str) -> str:
    return md_to_html(strip_latex(text))


async def send_html(update: Update, text: str, reply_markup=None):
    """Отправляет HTML, разбивая если > 4096 символов."""
    if len(text) <= TELEGRAM_LIMIT:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup)
        return
    chunks = []
    while len(text) > TELEGRAM_LIMIT:
        i = text.rfind("\n\n", 0, TELEGRAM_LIMIT)
        if i == -1: i = text.rfind("\n", 0, TELEGRAM_LIMIT)
        if i == -1: i = TELEGRAM_LIMIT
        chunks.append(text[:i])
        text = text[i:].lstrip()
    chunks.append(text)
    for n, chunk in enumerate(chunks):
        kb = reply_markup if n == len(chunks) - 1 else None
        await update.message.reply_text(chunk, parse_mode="HTML", reply_markup=kb)
