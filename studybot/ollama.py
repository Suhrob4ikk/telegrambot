import time
import asyncio
import logging

import httpx

from config import (
    OLLAMA_URL, MODEL_PRIMARY, MODEL_FALLBACK,
    MAX_HISTORY, RETRY_ATTEMPTS, RETRY_DELAY,
)

log = logging.getLogger("studybot")


async def _call(model: str, messages: list) -> tuple:
    payload = {
        "model": model, "messages": messages, "stream": False,
        "options": {"num_predict": 500, "temperature": 0.6, "top_p": 0.9},
    }
    t0 = time.time()
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
    return r.json()["message"]["content"].strip(), round(time.time() - t0, 1)


async def ask(system: str, history: list, user_text: str) -> tuple:
    """Retry + fallback. Возвращает (answer, elapsed, model_or_None)."""
    msgs = [{"role": "system", "content": system}]
    msgs += history[-MAX_HISTORY:]
    msgs.append({"role": "user", "content": user_text})
    last_err = None

    for model in [MODEL_PRIMARY, MODEL_FALLBACK]:
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            try:
                ans, elapsed = await _call(model, msgs)
                log.info(f"OK | model={model} | {elapsed}s | attempt={attempt}")
                return ans, elapsed, model
            except httpx.ConnectError as e:
                last_err = e
                log.warning(f"ConnectError | model={model}")
                break
            except httpx.TimeoutException as e:
                last_err = e
                log.warning(f"Timeout | model={model} | attempt={attempt}")
                if attempt < RETRY_ATTEMPTS:
                    await asyncio.sleep(RETRY_DELAY)
            except Exception as e:
                last_err = e
                log.error(f"Error | model={model} | {e}")
                if attempt < RETRY_ATTEMPTS:
                    await asyncio.sleep(RETRY_DELAY)

    if isinstance(last_err, httpx.ConnectError):
        return "❌ Ollama не запущена. Запусти: ollama serve", 0, None
    if isinstance(last_err, httpx.TimeoutException):
        return "⏳ Модель не ответила. Попробуй короче.", 0, None
    return "❌ Ошибка соединения. Попробуй позже.", 0, None
