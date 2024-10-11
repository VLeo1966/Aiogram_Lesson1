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

# Инициализация логирования для отслеживания работы бота и отладки
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

# Создание клавиатуры для меню
keyboards = ReplyKeyboardMarkup(
    keyboard=[
        [button_registr, button_exchange_rates],
        [button_tips, button_finances]
    ],
    resize_keyboard=True  # Автоматическое изменение размера клавиатуры под экран
)

# Подключение к базе данных SQLite
conn = sqlite3.connect('user.db')
cursor = conn.cursor()

# Создание таблицы users, если она не существует
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

# Определение классов состояний для FSM
class FinancesForm(StatesGroup):
    category1 = State()
    expenses1 = State()
    category2 = State()
    expenses2 = State()
    category3 = State()
    expenses3 = State()

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
    await state.set_state(FinancesForm.category1)
    await message.reply("Введите первую категорию расходов:")
    logger.info(f"Пользователь {message.from_user.id} начал ввод личных финансов.")

# Обработчик ввода первой категории расходов
@dp.message(FinancesForm.category1)
async def set_category1(message: Message, state: FSMContext):
    """
    Сохраняет первую категорию расходов и переходит к вводу расходов для нее.
    """
    await state.update_data(category1=message.text)
    await state.set_state(FinancesForm.expenses1)
    await message.reply("Введите расходы для категории 1:")
    logger.info(f"Пользователь {message.from_user.id} ввел категорию 1: {message.text}")

# Обработчик ввода расходов для первой категории
@dp.message(FinancesForm.expenses1)
async def set_expenses1(message: Message, state: FSMContext):
    """
    Сохраняет расходы для первой категории и переходит к вводу второй категории.
    """
    try:
        expenses1 = float(message.text.replace(',', '.'))  # Замена запятой на точку для корректного преобразования
        await state.update_data(expenses1=expenses1)
        await state.set_state(FinancesForm.category2)
        await message.reply("Введите вторую категорию расходов:")
        logger.info(f"Пользователь {message.from_user.id} ввел расходы для категории 1: {expenses1}")
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
    await state.set_state(FinancesForm.expenses2)
    await message.reply("Введите расходы для категории 2:")
    logger.info(f"Пользователь {message.from_user.id} ввел категорию 2: {message.text}")

# Обработчик ввода расходов для второй категории
@dp.message(FinancesForm.expenses2)
async def set_expenses2(message: Message, state: FSMContext):
    """
    Сохраняет расходы для второй категории и переходит к вводу третьей категории.
    """
    try:
        expenses2 = float(message.text.replace(',', '.'))
        await state.update_data(expenses2=expenses2)
        await state.set_state(FinancesForm.category3)
        await message.reply("Введите третью категорию расходов:")
        logger.info(f"Пользователь {message.from_user.id} ввел расходы для категории 2: {expenses2}")
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
    await state.set_state(FinancesForm.expenses3)
    await message.reply("Введите расходы для категории 3:")
    logger.info(f"Пользователь {message.from_user.id} ввел категорию 3: {message.text}")

# Обработчик ввода расходов для третьей категории и сохранение данных в БД
@dp.message(FinancesForm.expenses3)
async def set_expenses3(message: Message, state: FSMContext):
    """
    Сохраняет расходы для третьей категории, собирает все данные из FSM и обновляет запись пользователя в БД.
    """
    try:
        expenses3 = float(message.text.replace(',', '.'))
        await state.update_data(expenses3=expenses3)

        data = await state.get_data()
        telegram_id = message.from_user.id

        # Логирование данных для отладки
        logger.info(f"Сохраняем данные для пользователя {telegram_id}: {data}")

        try:
            # Выполнение SQL-запроса на обновление данных пользователя
            cursor.execute(
                '''UPDATE users 
                   SET category1 = ?, expenses1 = ?, 
                       category2 = ?, expenses2 = ?, 
                       category3 = ?, expenses3 = ? 
                   WHERE telegram_id = ?''',
                (
                    data.get('category1'), data.get('expenses1'),
                    data.get('category2'), data.get('expenses2'),
                    data.get('category3'), data.get('expenses3'),
                    telegram_id
                )
            )
            conn.commit()
            await message.answer("Категории и расходы сохранены!")
            logger.info(f"Данные пользователя {telegram_id} успешно сохранены в БД.")
        except sqlite3.Error as e:
            logger.error(f"Ошибка при обновлении данных пользователя {telegram_id}: {e}")
            await message.answer("Произошла ошибка при сохранении данных. Попробуйте позже.")

        # Очистка состояния FSM после завершения процесса
        await state.clear()
    except ValueError:
        await message.reply("Пожалуйста, введите корректную сумму расходов для категории 3.")
        logger.warning(f"Пользователь {message.from_user.id} ввел некорректные расходы для категории 3: {message.text}")

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
