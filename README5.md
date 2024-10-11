Конечно! Давайте модифицируем вашу программу таким образом, чтобы новые данные добавлялись в базу данных без удаления или перезаписи старых. Для этого потребуется изменить структуру базы данных и соответствующим образом обновить код бота.

### Шаги для реализации:

1. **Изменение структуры базы данных:**
   - **Текущая структура**: Таблица `users` содержит поля `category1`, `category2`, `category3`, `expenses1`, `expenses2`, `expenses3`. Это ограничивает пользователя вводом только трех категорий и расходов.
   - **Новая структура**: Создадим отдельную таблицу `finances`, которая будет хранить каждую запись расходов отдельно. Это позволит сохранять неограниченное количество категорий и расходов для каждого пользователя.

2. **Модификация кода бота:**
   - **Регистрация пользователя**: Оставим как есть, только добавим получение `id` пользователя из таблицы `users`.
   - **Ввод финансовых данных**: После ввода всех категорий и расходов будем вставлять каждую категорию и расход как отдельную запись в таблицу `finances`.

3. **Обработка данных:**
   - Убедимся, что новые данные добавляются в базу данных без удаления старых.
   - Добавим возможность просматривать все введенные финансовые данные.

### Обновленная Структура Базы Данных

Добавим новую таблицу `finances` для хранения финансовых записей:

```sql
CREATE TABLE IF NOT EXISTS finances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    expense REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);
```

### Полный Обновленный Код Бота на Aiogram с Подробными Комментариями

```python
import asyncio
import random
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

import sqlite3
import requests

# Импортируем токен из конфигурационного файла
from config4 import TOKEN

# Настройка логирования для отслеживания работы бота и отладки
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера с использованием MemoryStorage для FSM
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Определение кнопок для основного меню
button_registr = KeyboardButton(text="Регистрация в телеграм боте")
button_exchange_rates = KeyboardButton(text="Курс валют")
button_tips = KeyboardButton(text="Советы по экономии")
button_finances = KeyboardButton(text="Личные финансы")
button_view_finances = KeyboardButton(text="Просмотреть финансы")  # Новая кнопка для просмотра финансов

# Создание клавиатуры для меню
keyboards = ReplyKeyboardMarkup(
    keyboard=[
        [button_registr, button_exchange_rates],
        [button_tips, button_finances],
        [button_view_finances]  # Добавляем новую кнопку в клавиатуру
    ],
    resize_keyboard=True  # Автоматическое изменение размера клавиатуры под экран
)

# Подключение к базе данных SQLite
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# Создание таблицы users, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER UNIQUE,
    name TEXT
)
''')

# Создание таблицы finances, если она не существует
cursor.execute('''
CREATE TABLE IF NOT EXISTS finances (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    expense REAL,
    date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

conn.commit()

# Определение классов состояний для FSM
class FinancesForm(StatesGroup):
    category1 = State()
    expense1 = State()
    category2 = State()
    expense2 = State()
    category3 = State()
    expense3 = State()

# Обработчик команды /start
@dp.message(Command('start'))
async def send_start(message: Message):
    """
    Отправляет приветственное сообщение и показывает главное меню.
    """
    await message.answer(
        "Привет! Я ваш личный финансовый помощник. Выберите одну из опций в меню:",
        reply_markup=keyboards
    )
    logger.info(f"Пользователь {message.from_user.id} запустил бота.")

# Обработчик кнопки "Регистрация в телеграм боте"
@dp.message(F.text == "Регистрация в телеграм боте")
async def registration(message: Message):
    """
    Регистрирует пользователя в базе данных, если он еще не зарегистрирован.
    """
    telegram_id = message.from_user.id
    name = message.from_user.full_name

    # Проверка, зарегистрирован ли пользователь
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()

    if user:
        await message.answer("Вы уже зарегистрированы!")
        logger.info(f"Пользователь {telegram_id} уже зарегистрирован.")
    else:
        try:
            # Вставка нового пользователя в базу данных
            cursor.execute('''INSERT INTO users (telegram_id, name) VALUES (?, ?)''', (telegram_id, name))
            conn.commit()
            await message.answer("Вы успешно зарегистрированы!")
            logger.info(f"Пользователь {telegram_id} успешно зарегистрирован.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при регистрации пользователя {telegram_id}: {e}")
            await message.answer("Произошла ошибка при регистрации. Попробуйте позже.")

# Обработчик кнопки "Курс валют"
@dp.message(F.text == "Курс валют")
async def exchange_rates(message: Message):
    """
    Получает и отправляет пользователю текущие курсы валют USD и EUR к RUB.
    """
    url = "https://v6.exchangerate-api.com/v6/09edf8b2bb246e1f801cbfba/latest/USD"
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            await message.answer("Не удалось получить данные о курсе валют!")
            logger.warning(f"Не удалось получить курс валют: статус {response.status_code}")
            return

        usd_to_rub = data['conversion_rates']['RUB']
        eur_to_usd = data['conversion_rates']['EUR']
        euro_to_rub = eur_to_usd * usd_to_rub

        await message.answer(f"1 USD - {usd_to_rub:.2f} RUB\n"
                             f"1 EUR - {euro_to_rub:.2f} RUB")
        logger.info(f"Отправлены курсы валют пользователю {message.from_user.id}")
    except Exception as e:
        logger.error(f"Ошибка при получении курса валют: {e}")
        await message.answer("Произошла ошибка при получении курса валют.")

# Обработчик кнопки "Советы по экономии"
@dp.message(F.text == "Советы по экономии")
async def send_tips(message: Message):
    """
    Отправляет случайный совет по экономии из списка.
    """
    tips = [
        "Совет 1: Ведите бюджет и следите за своими расходами.",
        "Совет 2: Откладывайте часть доходов на сбережения.",
        "Совет 3: Покупайте товары по скидкам и распродажам."
    ]
    tip = random.choice(tips)
    await message.answer(tip)
    logger.info(f"Отправлен совет пользователю {message.from_user.id}")

# Обработчик кнопки "Личные финансы" - начало процесса ввода данных
@dp.message(F.text == "Личные финансы")
async def start_finances(message: Message, state: FSMContext):
    """
    Начинает процесс ввода личных финансов, устанавливая состояние для первой категории.
    """
    # Проверка регистрации пользователя перед вводом финансов
    telegram_id = message.from_user.id
    cursor.execute('''SELECT * FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer("Пожалуйста, зарегистрируйтесь сначала.")
        logger.info(f"Пользователь {telegram_id} попытался ввести финансы без регистрации.")
        return

    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")
    logger.info(f"Пользователь {telegram_id} начал ввод личных финансов.")

# Обработчик ввода первой категории расходов
@dp.message(FinancesForm.category1)
async def set_category1(message: Message, state: FSMContext):
    """
    Сохраняет первую категорию расходов и переходит к вводу расходов для нее.
    """
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expense1)
    await message.reply("Введите расходы для категории 1:")
    logger.info(f"Пользователь {message.from_user.id} ввел категорию 1: {message.text}")

# Обработчик ввода расходов для первой категории
@dp.message(FinancesForm.expense1)
async def set_expense1(message: Message, state: FSMContext):
    """
    Сохраняет расходы для первой категории и переходит к вводу второй категории.
    """
    try:
        # Замена запятой на точку для корректного преобразования
        expense1 = float(message.text.replace(',', '.'))
        await state.update_data(expense1=expense1)
        await state.set_state(FinancesForm.category2)
        await message.reply("Введите вторую категорию расходов:")
        logger.info(f"Пользователь {message.from_user.id} ввел расходы для категории 1: {expense1}")
    except ValueError:
        await message.reply("Пожалуйста, введите корректную сумму расходов для категории 1.")
        logger.warning(f"Пользователь {message.from_user.id} ввел некорректные расходы для категории 1: {message.text}")

# Обработчик ввода второй категории расходов
@dp.message(FinancesForm.category2)
async def set_category2(message: Message, state: FSMContext):
    """
    Сохраняет вторую категорию расходов и переходит к вводу расходов для нее.
    """
    await state.update_data(category2=message.text)
    await state.set_state(FinancesForm.expense2)
    await message.reply("Введите расходы для категории 2:")
    logger.info(f"Пользователь {message.from_user.id} ввел категорию 2: {message.text}")

# Обработчик ввода расходов для второй категории
@dp.message(FinancesForm.expense2)
async def set_expense2(message: Message, state: FSMContext):
    """
    Сохраняет расходы для второй категории и переходит к вводу третьей категории.
    """
    try:
        expense2 = float(message.text.replace(',', '.'))
        await state.update_data(expense2=expense2)
        await state.set_state(FinancesForm.category3)
        await message.reply("Введите третью категорию расходов:")
        logger.info(f"Пользователь {message.from_user.id} ввел расходы для категории 2: {expense2}")
    except ValueError:
        await message.reply("Пожалуйста, введите корректную сумму расходов для категории 2.")
        logger.warning(f"Пользователь {message.from_user.id} ввел некорректные расходы для категории 2: {message.text}")

# Обработчик ввода третьей категории расходов
@dp.message(FinancesForm.category3)
async def set_category3(message: Message, state: FSMContext):
    """
    Сохраняет третью категорию расходов и переходит к вводу расходов для нее.
    """
    await state.update_data(category3=message.text)
    await state.set_state(FinancesForm.expense3)
    await message.reply("Введите расходы для категории 3:")
    logger.info(f"Пользователь {message.from_user.id} ввел категорию 3: {message.text}")

# Обработчик ввода расходов для третьей категории и сохранение данных в БД
@dp.message(FinancesForm.expense3)
async def set_expense3(message: Message, state: FSMContext):
    """
    Сохраняет расходы для третьей категории, собирает все данные из FSM и добавляет их в таблицу finances.
    """
    try:
        expense3 = float(message.text.replace(',', '.'))
        await state.update_data(expense3=expense3)

        data = await state.get_data()
        telegram_id = message.from_user.id

        # Получение user_id из таблицы users
        cursor.execute('''SELECT id FROM users WHERE telegram_id = ?''', (telegram_id,))
        user = cursor.fetchone()
        if not user:
            await message.answer("Пользователь не найден. Пожалуйста, зарегистрируйтесь.")
            logger.error(f"Пользователь {telegram_id} не найден при сохранении финансов.")
            await state.clear()
            return

        user_id = user[0]

        # Логирование данных для отладки
        logger.info(f"Сохраняем данные для пользователя {telegram_id}: {data}")

        # Подготовка данных для вставки
        categories = [data.get('category1'), data.get('category2'), data.get('category3')]
        expenses = [data.get('expense1'), data.get('expense2'), data.get('expense3')]

        try:
            # Вставка каждой категории и расхода как отдельной записи в таблицу finances
            for category, expense in zip(categories, expenses):
                cursor.execute(
                    '''INSERT INTO finances (user_id, category, expense) VALUES (?, ?, ?)''',
                    (user_id, category, expense)
                )
            conn.commit()
            await message.answer("Категории и расходы сохранены!")
            logger.info(f"Данные пользователя {telegram_id} успешно сохранены в БД.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при сохранении данных пользователя {telegram_id}: {e}")
            await message.answer("Произошла ошибка при сохранении данных. Попробуйте позже.")

        # Очистка состояния FSM после завершения процесса
        await state.clear()
    except ValueError:
        await message.reply("Пожалуйста, введите корректную сумму расходов для категории 3.")
        logger.warning(f"Пользователь {message.from_user.id} ввел некорректные расходы для категории 3: {message.text}")

# Обработчик кнопки "Просмотреть финансы"
@dp.message(F.text == "Просмотреть финансы")
async def view_finances(message: Message):
    """
    Позволяет пользователю просмотреть все введенные финансовые данные.
    """
    telegram_id = message.from_user.id

    # Получение user_id из таблицы users
    cursor.execute('''SELECT id FROM users WHERE telegram_id = ?''', (telegram_id,))
    user = cursor.fetchone()

    if not user:
        await message.answer("Пожалуйста, зарегистрируйтесь сначала.")
        logger.info(f"Пользователь {telegram_id} попытался просмотреть финансы без регистрации.")
        return

    user_id = user[0]

    # Получение всех финансовых записей пользователя
    cursor.execute('''SELECT category, expense, date FROM finances WHERE user_id = ? ORDER BY date DESC''', (user_id,))
    finances = cursor.fetchall()

    if not finances:
        await message.answer("У вас пока нет записей финансов.")
        logger.info(f"Пользователь {telegram_id} попытался просмотреть финансы, но записей нет.")
        return

    # Формирование сообщения с финансовыми данными
    response = "Ваши финансы:\n\n"
    for fin in finances:
        category, expense, date = fin
        response += f"Категория: {category}\nСумма: {expense} RUB\nДата: {date}\n\n"

    await message.answer(response)
    logger.info(f"Пользователь {telegram_id} просмотрел свои финансы.")

# Обработчик завершения работы бота для закрытия соединения с БД и бота
async def on_shutdown(dp: Dispatcher):
    """
    Обработчик завершения работы бота. Закрывает соединение с базой данных и ботом.
    """
    cursor.close()
    conn.close()
    await bot.close()
    logger.info("Бот был корректно остановлен.")

# Основная функция запуска бота
async def main():
    """
    Основная функция для запуска бота. Запускает polling и обрабатывает исключения.
    """
    try:
        logger.info("Бот стартовал.")
        await dp.start_polling(bot, on_shutdown=on_shutdown)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Бот остановлен пользователем.")

# Точка входа в программу
if __name__ == '__main__':
    asyncio.run(main())
```

### Пояснения к Внесенным Изменениям

1. **Создание Таблицы `finances`:**
   - Добавлена новая таблица `finances`, которая хранит каждую запись финансов отдельно.
   - Поля:
     - `id`: Уникальный идентификатор записи.
     - `user_id`: Идентификатор пользователя из таблицы `users`.
     - `category`: Название категории расходов.
     - `expense`: Сумма расходов.
     - `date`: Дата и время записи (автоматически заполняется текущим временем).

2. **Добавление Кнопки "Просмотреть финансы":**
   - Добавлена новая кнопка `button_view_finances` для просмотра всех финансовых записей пользователя.

3. **Регистрация Пользователя:**
   - При регистрации теперь сохраняется только `telegram_id` и `name`. Финансовые данные хранятся отдельно в таблице `finances`.

4. **Ввод Финансовых Данных:**
   - Пользователь вводит три категории и соответствующие им расходы.
   - После ввода всех данных каждая категория и расход сохраняются как отдельная запись в таблице `finances`, связанной с `user_id` пользователя.
   - Таким образом, новые данные добавляются без удаления старых.

5. **Просмотр Финансовых Данных:**
   - Пользователь может просмотреть все свои финансовые записи, выбрав кнопку "Просмотреть финансы".
   - Бот извлекает все записи из таблицы `finances`, связанные с `user_id` пользователя, и отображает их в удобном формате.

6. **Обработка Исключений и Логирование:**
   - Добавлена обработка ошибок при взаимодействии с базой данных.
   - Логирование добавлено для отслеживания действий пользователей и возможных ошибок.

### Дополнительные Рекомендации

1. **Асинхронный Доступ к Базе Данных:**
   - В текущей реализации используется синхронный модуль `sqlite3`, который может блокировать работу бота при выполнении запросов к базе данных.
   - Для улучшения производительности рекомендуется использовать асинхронные библиотеки, такие как `aiosqlite`.
   - **Пример использования `aiosqlite`:**
     ```python
     import aiosqlite

     async with aiosqlite.connect('user.db') as db:
         await db.execute('YOUR SQL QUERY', params)
         await db.commit()
     ```

2. **Валидация Входных Данных:**
   - Помимо проверки на `ValueError`, можно добавить более продвинутую валидацию, например, проверку на отрицательные значения расходов или максимальные лимиты.

3. **Улучшение Безопасности:**
   - Избегайте хранения чувствительных данных в открытом виде. Рассмотрите возможность шифрования или других методов защиты данных пользователей.

4. **Оптимизация SQL Запросов:**
   - Используйте параметризованные запросы для предотвращения SQL-инъекций (что уже реализовано в вашем коде).

5. **Разделение Кода на Модули:**
   - Для улучшения читаемости и поддержки кода можно разделить его на несколько модулей, например, отдельно обрабатывать базы данных, FSM, обработчики команд и т.д.

### Тестирование Обновленной Программы

1. **Регистрация Пользователя:**
   - Отправьте команду `/start` и выберите опцию "Регистрация в телеграм боте".
   - Убедитесь, что пользователь успешно зарегистрирован и данные сохранены в таблице `users`.

2. **Ввод Финансовых Данных:**
   - Выберите опцию "Личные финансы" и последовательно вводите три категории и соответствующие им расходы.
   - Проверьте, что данные корректно добавляются в таблицу `finances`.

3. **Просмотр Финансовых Данных:**
   - Выберите опцию "Просмотреть финансы" и убедитесь, что все введенные финансовые записи отображаются правильно.

4. **Проверка Базы Данных:**
   - Откройте `user.db` с помощью SQLite браузера или другого инструмента и убедитесь, что данные сохраняются правильно в таблицах `users` и `finances`.

### Заключение

Теперь ваша программа позволяет добавлять новые финансовые данные без удаления старых, обеспечивая гибкость и масштабируемость. Пользователи могут вводить неограниченное количество категорий и расходов, а также просматривать всю историю своих финансовых записей. Если у вас возникнут дополнительные вопросы или потребуется дальнейшая помощь, не стесняйтесь обращаться!