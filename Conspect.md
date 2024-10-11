### Лекция: Разработка чат-ботов в Telegram на Python с использованием Aiogram

---

#### **Тема 11: Разработка чат-ботов в Telegram**

---

#### **Цели урока:**
1. Разработать кейс "Финансовый бот-помощник".
2. Закрепить знания, полученные в модуле по Telegram-ботам.

---

#### **1. Подготовка к разработке**

- **Интерфейсы современных приложений:** Быстро меняются. В случае несоответствия интерфейса материала с текущим интерфейсом, обратиться в учебный чат с указанием номера урока и видео.

- **Инструменты:**
  - **PyCharm:** Среда разработки для написания кода.
  - **SQLite:** База данных для хранения информации о пользователях.

---

#### **2. Начальная настройка проекта**

- **Импорт необходимых библиотек:**
  ```python
  import asyncio
  from aiogram import Bot, Dispatcher, F
  from aiogram.filters import CommandStart, Command
  from aiogram.types import Message, FSInputFile
  from aiogram.fsm.context import FSMContext
  from aiogram.fsm.state import State, StatesGroup
  from aiogram.fsm.storage.memory import MemoryStorage

  from config import TOKEN  # Импортируем токен из конфигурационного файла
  import sqlite3
  import aiohttp
  import logging
  ```

- **Инициализация бота и диспетчера:**
  ```python
  bot = Bot(token=TOKEN)
  dp = Dispatcher()
  
  logging.basicConfig(level=logging.INFO)
  ```

- **Удаление неиспользуемых ключей:**
  Удалить `WEATHER_API_KEY`, так как бот не будет работать с погодой.

---

#### **3. Создание интерфейса пользователя**

- **Импорт библиотек для работы с клавиатурами:**
  ```python
  from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
  from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
  ```

- **Создание кнопок:**
  ```python
  button_registr = KeyboardButton(text="Регистрация в телеграм-боте")
  button_exchange_rates = KeyboardButton(text="Курс валют")
  button_tips = KeyboardButton(text="Советы по экономии")
  button_finances = KeyboardButton(text="Личные финансы")
  ```

- **Создание клавиатуры:**
  ```python
  keyboard = ReplyKeyboardMarkup(
      keyboard=[
          [button_registr, button_exchange_rates],
          [button_tips, button_finances]
      ],
      resize_keyboard=True  # Автоматическое изменение размера клавиатуры под экран
  )
  ```

---

#### **4. Настройка базы данных**

- **Подключение к SQLite и создание таблицы `users`:**
  ```python
  conn = sqlite3.connect('user.db')
  cursor = conn.cursor()

  cursor.execute('''
  CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY,
      telegram_id INTEGER UNIQUE,
      name TEXT,
      category1 TEXT,
      category2 TEXT,
      category3 TEXT,
      expenses1 REAL,
      expenses2 REAL,
      expenses3 REAL
      )
  ''')
  conn.commit()
  ```

---

#### **5. Определение состояний FSM (Машина состояний)**

- **Создание класса состояний для ввода финансовых данных:**
  ```python
  class FinancesForm(StatesGroup):
      category1 = State()
      expenses1 = State()
      category2 = State()
      expenses2 = State()
      category3 = State()
      expenses3 = State()
  ```

---

#### **6. Реализация функций бота**

##### **6.1. Функция приветствия и отображение меню**

- **Обработчик команды `/start`:**
  ```python
  @dp.message(Command('start'))
  async def send_start(message: Message):
      await message.answer(
          "Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:",
          reply_markup=keyboard
      )
  ```
  - **Описание:** Отправляет приветственное сообщение и показывает главное меню с кнопками.

##### **6.2. Регистрация пользователя**

- **Обработчик кнопки "Регистрация в телеграм-боте":**
  ```python
  @dp.message(F.text == "Регистрация в телеграм-боте")
  async def registration(message: Message):
      telegram_id = message.from_user.id
      name = message.from_user.full_name
      cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
      user = cursor.fetchone()
      if user:
          await message.answer("Вы уже зарегистрированы!")
      else:
          cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
          conn.commit()
          await message.answer("Вы успешно зарегистрированы!")
  ```
  - **Описание:** Проверяет, зарегистрирован ли пользователь. Если нет, добавляет его в базу данных.

##### **6.3. Получение курса валют**

- **Обработчик кнопки "Курс валют":**
  ```python
  @dp.message(F.text == "Курс валют")
  async def exchange_rates(message: Message):
      url = "https://v6.exchangerate-api.com/v6/09edf8b2bb246e1f801cbfba/latest/USD"
      try:
          response = requests.get(url)
          data = response.json()
          if response.status_code != 200:
              await message.answer("Не удалось получить данные о курсе валют!")
              return
          usd_to_rub = data['conversion_rates']['RUB']
          eur_to_usd = data['conversion_rates']['EUR']
          euro_to_rub = eur_to_usd * usd_to_rub
          await message.answer(f"1 USD - {usd_to_rub:.2f} RUB\n"
                               f"1 EUR - {euro_to_rub:.2f} RUB")
      except:
          await message.answer("Произошла ошибка")
  ```
  - **Описание:** Получает актуальные курсы валют USD и EUR к RUB с помощью API и отправляет их пользователю.

##### **6.4. Отправка советов по экономии**

- **Обработчик кнопки "Советы по экономии":**
  ```python
  @dp.message(F.text == "Советы по экономии")
  async def send_tips(message: Message):
      tips = [
          "Совет 1: Ведите бюджет и следите за своими расходами.",
          "Совет 2: Откладывайте часть доходов на сбережения.",
          "Совет 3: Покупайте товары по скидкам и распродажам."
      ]
      tip = random.choice(tips)
      await message.answer(tip)
  ```
  - **Описание:** Отправляет случайный совет по экономии из заранее подготовленного списка.

##### **6.5. Ведение учёта личных финансов**

- **Обработчик кнопки "Личные финансы":**
  ```python
  @dp.message(F.text == "Личные финансы")
  async def finances(message: Message, state: FSMContext):
      await state.set_state(FinancesForm.category1)
      await message.reply("Введите первую категорию расходов:")
  ```
  - **Описание:** Начинает процесс ввода финансовых данных, устанавливая первое состояние для ввода категории.

- **Последовательные обработчики для ввода категорий и расходов:**
  
  1. **Ввод первой категории:**
     ```python
     @dp.message(FinancesForm.category1)
     async def finances(message: Message, state: FSMContext):
         await state.update_data(category1=message.text)
         await state.set_state(FinancesForm.expenses1)
         await message.reply("Введите расходы для категории 1:")
     ```
  
  2. **Ввод расходов для первой категории:**
     ```python
     @dp.message(FinancesForm.expenses1)
     async def finances(message: Message, state: FSMContext):
         await state.update_data(expenses1=float(message.text))
         await state.set_state(FinancesForm.category2)
         await message.reply("Введите вторую категорию расходов:")
     ```
  
  3. **Ввод второй категории:**
     ```python
     @dp.message(FinancesForm.category2)
     async def finances(message: Message, state: FSMContext):
         await state.update_data(category2=message.text)
         await state.set_state(FinancesForm.expenses2)
         await message.reply("Введите расходы для категории 2:")
     ```
  
  4. **Ввод расходов для второй категории:**
     ```python
     @dp.message(FinancesForm.expenses2)
     async def finances(message: Message, state: FSMContext):
         await state.update_data(expenses2=float(message.text))
         await state.set_state(FinancesForm.category3)
         await message.reply("Введите третью категорию расходов:")
     ```
  
  5. **Ввод третьей категории:**
     ```python
     @dp.message(FinancesForm.category3)
     async def finances(message: Message, state: FSMContext):
         await state.update_data(category3=message.text)
         await state.set_state(FinancesForm.expenses3)
         await message.reply("Введите расходы для категории 3:")
     ```
  
  6. **Ввод расходов для третьей категории и сохранение данных:**
     ```python
     @dp.message(FinancesForm.expenses3)
     async def finances(message: Message, state: FSMContext):
         data = await state.get_data()
         telegram_id = message.from_user.id
         cursor.execute('''UPDATE users SET category1 = ?, expenses1 = ?, category2 = ?, expenses2 = ?, category3 = ?, expenses3 = ? WHERE telegram_id = ?''',
                        (data['category1'], data['expenses1'], data['category2'], data['expenses2'], data['category3'], float(message.text), telegram_id))
         conn.commit()
         await state.clear()
         await message.answer("Категории и расходы сохранены!")
     ```
     - **Описание:** После ввода всех категорий и расходов обновляет запись пользователя в базе данных и очищает состояние FSM.

---

#### **7. Запуск бота**

- **Основная функция для запуска бота:**
  ```python
  async def main():
      await dp.start_polling(bot)
  
  if __name__ == '__main__':
      asyncio.run(main())
  ```
  - **Описание:** Запускает процесс polling для бота, позволяя ему принимать и обрабатывать сообщения от пользователей.

---

#### **8. Тестирование**

- **Запуск программы:** Проверить работу бота, отправляя команды и нажимая на кнопки.
- **Проверка базы данных:** Убедиться, что данные пользователей и их финансовые записи корректно сохраняются в `user.db`.

---

#### **Результаты урока:**

1. **Разработан кейс "Финансовый бот-помощник".**
2. **Закреплены знания по созданию Telegram-ботов с использованием aiogram.**

---

#### **Дополнительные материалы:**

- **API для получения курса валют:** [exchangerate-api.com](https://www.exchangerate-api.com/)
- **Пример кода:** 
  - [GitHub - bot.py](https://github.com/VLeo1966/Aiogram_Lesson1/blob/main/bot.py)
  - [GitHub - fin_bot2.py](https://github.com/VLeo1966/Aiogram_Lesson1/blob/main/fin_bot2.py)

---

#### **Задание:**

- **Повторить все действия эксперта и загрузить проект в GIT.**
- **Следующее занятие:** Начало работы с автоматическими тестами.

---

#### **Советы по работе с кодом:**

- **Организация функций:** Убедитесь, что каждая функция имеет уникальное имя, чтобы избежать перезаписи и конфликтов.
- **Обработка ошибок:** Используйте конструкции `try-except` для обработки возможных ошибок при работе с API и базой данных.
- **Логирование:** Включите логирование для отслеживания действий пользователей и выявления потенциальных проблем.
- **Хранение конфиденциальных данных:** Никогда не храните токены и API-ключи в открытом виде. Используйте отдельные конфигурационные файлы или переменные окружения.
- **Асинхронность:** Рассмотрите использование асинхронных библиотек для работы с базой данных (например, `aiosqlite`) для повышения производительности бота.

---

#### **Пример структуры проекта:**

```
Aiogram_Lesson5/
│
├── bot.py
├── fin_bot2.py
├── config.py
├── user.db
├── README.md
└── requirements.txt
```

- **bot.py и fin_bot2.py:** Основные скрипты бота.
- **config.py:** Файл с конфигурационными данными (токен, API-ключи).
- **user.db:** SQLite база данных.
- **README.md:** Описание проекта.
- **requirements.txt:** Список зависимостей проекта.

---

#### **Заключение:**

В этом уроке вы научились создавать Telegram-бота с возможностью регистрации пользователей, получения актуальных курсов валют, предоставления советов по экономии и ведения учёта личных финансов. Эти навыки являются основой для разработки более сложных и функциональных ботов в будущем.

Если возникнут вопросы или трудности, обращайтесь в учебный чат для получения помощи.

---