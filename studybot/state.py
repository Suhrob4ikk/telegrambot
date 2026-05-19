from dataclasses import dataclass, field
from datetime import datetime

from telegram.ext import ContextTypes


# ── FSM quiz states ─────────────────────────────────────────────
QUIZ_OFF   = "off"
QUIZ_ASKED = "asked"


@dataclass
class QuizState:
    active:       bool = False
    topic:        str  = ""
    current_q:    str  = ""
    question_num: int  = 0


@dataclass
class UserStats:
    total_messages: int = 0
    quiz_sessions:  int = 0
    joined:         str = field(default_factory=lambda: datetime.now().strftime("%d.%m.%Y"))
    errors:         int = 0

    def format(self) -> str:
        lines = [
            "<b>📊 Statistics</b>\n",
            f"📅 Using since: {self.joined}",
            f"💬 Total messages: {self.total_messages}",
            f"📝 Quiz sessions: {self.quiz_sessions}",
        ]
        if self.errors:
            lines.append(f"⚠️ Connection errors: {self.errors}")
        return "\n".join(lines)


@dataclass
class UserState:
    history: list      = field(default_factory=list)
    quiz:    QuizState = field(default_factory=QuizState)
    stats:   UserStats = field(default_factory=UserStats)

    def clear(self):
        """Очищает историю чата. Статистика и quiz не трогаются."""
        self.history = []
        self.quiz    = QuizState()

    def full_reset(self):
        """Полный сброс всего."""
        self.history = []
        self.quiz    = QuizState()
        self.stats   = UserStats()


def get_state(context: ContextTypes.DEFAULT_TYPE) -> UserState:
    if "state" not in context.user_data:
        context.user_data["state"] = UserState()
    return context.user_data["state"]
