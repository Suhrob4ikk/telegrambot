<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&height=200&color=0:0d0800,50:7c3000,100:0d0800&text=DonishAI&fontSize=52&fontColor=fde68a&animation=fadeIn&fontAlignY=52&desc=Учебный%20ассистент%20для%20студентов%20МГУ%20Душанбе&descSize=16&descAlignY=70&descColor=fb923c" width="100%" />

</div>

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Telegram](https://img.shields.io/badge/Telegram%20Bot-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Ollama](https://img.shields.io/badge/Ollama-000000?style=for-the-badge&logoColor=white)
![License](https://img.shields.io/badge/license-MIT-fb923c?style=for-the-badge)

</div>

---

## 📖 О проекте

**DonishAI** — Telegram-бот учебного ассистента для студентов МГУ (филиал в Душанбе).  
Работает на локальной нейросети через **Ollama** — без внешних API, без утечки данных.

> *"Donish"* (دانش) — знание на таджикском и персидском языках.

---

## ✨ Возможности

| Функция | Описание |
|---|---|
| 📐 Математика | Задачи, формулы, доказательства |
| 💻 Программирование | Python, C++, SQL — объяснение и отладка кода |
| ⚡ Физика | Задачи, законы, концепции |
| 🗄 Базы данных | SQL-запросы, проектирование схем |
| 🧠 Память диалога | Хранит до 20 сообщений истории |
| 🔒 Фильтрация | Отвечает только на учебные вопросы |

---

## 🛠 Стек

```
python-telegram-bot  — Telegram Bot API
httpx                — Асинхронные HTTP-запросы к Ollama
Ollama (qwen2.5:3b)  — Локальная LLM модель
python-dotenv        — Управление переменными окружения
```

---

## 🚀 Быстрый старт

### 1. Клонировать репозиторий
```bash
git clone https://github.com/Suhrob4ikk/telegrambot.git
cd telegrambot
```

### 2. Установить зависимости
```bash
pip install python-telegram-bot httpx python-dotenv
```

### 3. Установить и запустить Ollama
```bash
# Установка: https://ollama.com
ollama pull qwen2.5:3b
ollama serve
```

### 4. Создать файл `.env.donish`
```env
TELEGRAM_TOKEN=ваш_токен_от_BotFather
```

### 5. Запустить бота
```bash
python tbot.py
```

---

## ⚙️ Конфигурация

| Параметр | Значение | Описание |
|---|---|---|
| `MODEL` | `qwen2.5:3b` | Модель Ollama |
| `MAX_HISTORY` | `20` | Сообщений в памяти |
| `MAX_INPUT` | `2000` | Макс. символов от пользователя |
| `OLLAMA_URL` | `localhost:11434` | Адрес Ollama |

---

## 📁 Структура

```
telegrambot/
├── tbot.py          # Основной файл бота
├── .env.donish      # Токен (не коммитить!)
└── donishai.log     # Лог файл (генерируется)
```

---

## 🤖 Команды бота

| Команда | Описание |
|---|---|
| `/start` | Приветствие и главное меню |
| `/help` | Справка по возможностям |
| `/clear` | Очистить историю диалога |

---

## Автор

**Suhrob Davlatov** — студент 2-го курса, Прикладная математика и информатика  
Филиал МГУ в Душанбе

[![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)](https://t.me/davlatov3007)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/Suhrob4ikk)

---

<div align="center">
<img src="https://capsule-render.vercel.app/api?type=waving&height=100&color=0:0d0800,50:7c3000,100:0d0800&section=footer&animation=fadeIn" width="100%" />
</div>
