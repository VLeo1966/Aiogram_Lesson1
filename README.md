# Aiogram_Lesson1
```markdown
# Урок: Знакомство с библиотекой Aiogram и основы работы с Telegram API

## Теория на сегодня:
### Введение в Telegram-ботов и библиотеку aiogram

Сегодняшний урок посвящен созданию Telegram-ботов с использованием библиотеки `aiogram`, которая позволяет работать с Telegram Bot API асинхронно, эффективно обрабатывать команды, сообщения и другие типы обновлений. 

Многие уже знакомы с ботами и использовали библиотеку `Telebot`, но на этот раз мы рассмотрим более популярную и гибкую библиотеку `aiogram`.

## План урока:
1. Что такое `aiogram` и его использование.
2. Установка и настройка `aiogram`.
3. Основные методы работы с Telegram API.

---

### 1. Что такое aiogram?

`aiogram` — это асинхронная библиотека для создания ботов в мессенджере Telegram на Python. 

Основные возможности:
- Асинхронность — выполнение нескольких действий одновременно.
- Два метода работы с Telegram Bot API:
  - **Polling** — бот сам запрашивает данные от Telegram.
  - **Webhook** — Telegram отправляет данные боту по HTTP.

---

### 2. Преимущества aiogram:

- **Асинхронность** — эффективное использование ресурсов.
- **Гибкость** и простота в использовании.
- **Сообщество** и регулярные обновления.
- Возможность интеграции с другими сервисами и API.

---

### 3. Работа с aiogram:

#### Установка:
```bash
pip install aiogram
```

#### Импорт и настройка:
```python
import asyncio
from aiogram import Bot, Dispatcher

bot = Bot(token='YOUR_TOKEN')
dp = Dispatcher()

async def main():
    await dp.start_polling()
    
if __name__ == "__main__":
    asyncio.run(main())
```

#### Обработка команд:

1. Импортируем необходимые компоненты для обработки команд:
   ```python
   from aiogram.filters import CommandStart
   from aiogram.types import Message
   ```

2. Создаем обработчик для команды `/start`:
   ```python
   @dp.message(CommandStart())
   async def start(message: Message):
       await message.answer("Приветики, я бот!")
   ```

#### Создание бота в Telegram:

- Используем BotFather для создания бота.
- Получаем токен и добавляем его в код.
- Создаем файл `config.py` для хранения токена:
  ```python
  TOKEN = "YOUR_BOT_TOKEN"
  ```

---

### 4. Улучшение функционала:

#### Добавление команды `/help`:
```python
from aiogram.filters import Command

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды:\n/start\n/help")
```

#### Настройка команд через BotFather:
- Используем команду `/setcommands` в BotFather для добавления команд в меню бота.

---

### 5. Реакции на текст и фото:

#### Ответ на текстовые сообщения:
```python
from aiogram import F

@dp.message(F.text == "что такое ИИ?")
async def aitext(message: Message):
    await message.answer('Искусственный интеллект — это...')
```

#### Обработка фото:
```python
import random

@dp.message(F.photo)
async def react_photo(message: Message):
    responses = ['Ого, какая фотка!', 'Непонятно, что это такое']
    rand_response = random.choice(responses)
    await message.answer(rand_response)
```

#### Отправка фотографий:
```python
@dp.message(Command('photo'))
async def photo(message: Message):
    photos = ['URL_1', 'URL_2']
    rand_photo = random.choice(photos)
    await message.answer_photo(photo=rand_photo, caption='Это супер крутая картинка')
```

---

### 6. Итоги урока:
- Познакомились с библиотекой `aiogram` и её возможностями.
- Установили и настроили библиотеку.
- Научились обрабатывать команды и сообщения.
- Улучшили функционал бота, добавив ответы на текст и фото, а также команду `/help`.
```