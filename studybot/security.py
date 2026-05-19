import re

_INJECTION_RE = re.compile(
    r"ignore\s+(all\s+)?previous"
    r"|forget\s+(all\s+)?(instructions|rules|prompts)"
    r"|new\s+system\s+prompt"
    r"|(you\s+are\s+now|ты\s+теперь)\s+\w+"
    r"|забудь\s+(все\s+)?(инструкции|правила|промпт)"
    r"|(override|bypass)\s+(instructions|rules|safety)"
    r"|act\s+as\s+(if\s+you\s+are\s+)?\w+"
    r"|disregard\s+(all\s+)?(previous|instructions)"
    r"|^\s*system\s*:"
    r"|prompt\s+injection",
    re.IGNORECASE | re.MULTILINE,
)


def is_injection(text: str) -> bool:
    return bool(_INJECTION_RE.search(text))
