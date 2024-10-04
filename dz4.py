import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from aiogram.fsm.context import FSMContext
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Задание 1: Создание простого меню с кнопками
@dp.message(CommandStart())
async def start(message: Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Привет'), KeyboardButton(text='Пока')]
        ],
        resize_keyboard=True
    )
    await message.answer("Выберите опцию:", reply_markup=keyboard)

@dp.message(F.text == 'Привет')
async def say_goodbye(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}!')
@dp.message(F.text == 'Пока')
async def say_goodbye(message: Message):
    await message.answer(f'До свидания, {message.from_user.first_name}!')



# Задание 2: Кнопки с URL-ссылками
# Команда /links для отображения кнопок с URL-ссылками
@dp.message(Command('links'))
async def show_links(message: Message):
    # Создаем инлайн-клавиатуру с URL-ссылками
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Новости", url="https://dzen.ru/news")],
        [InlineKeyboardButton(text="Музыка", url="https://music.yandex.ru")],
        [InlineKeyboardButton(text="Видео", url="https://www.youtube.com")]
    ])

    # Отправляем сообщение с клавиатурой
    await message.answer("Выберите ссылку:", reply_markup=keyboard)

# Задание 3: Динамическое изменение клавиатуры
# Команда /dynamic для создания динамической клавиатуры
@dp.message(Command('dynamic'))
async def dynamic_keyboard(message: Message):
    # Создаем инлайн-клавиатуру с кнопкой "Показать больше"
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Показать больше", callback_data="show_more")]
    ])

    await message.answer("Нажмите на кнопку, чтобы показать больше опций:", reply_markup=keyboard)


# Обработка нажатия на кнопку "Показать больше"
@dp.callback_query(F.data == 'show_more')
async def show_more_options(callback_query: CallbackQuery):
    # Создаем новую клавиатуру с дополнительными опциями
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Опция 1", callback_data="option_1")],
        [InlineKeyboardButton(text="Опция 2", callback_data="option_2")]
    ])

    # Редактируем предыдущее сообщение с новой клавиатурой
    await callback_query.message.edit_text("Выберите опцию:", reply_markup=keyboard)


# Обработка выбора Опции 1
@dp.callback_query(F.data == 'option_1')
async def option_1_selected(callback_query: CallbackQuery):
    await callback_query.message.answer("Вы выбрали Опцию 1")


# Обработка выбора Опции 2
@dp.callback_query(F.data == 'option_2')
async def option_2_selected(callback_query: CallbackQuery):
    await callback_query.message.answer("Вы выбрали Опцию 2")

# Главная функция для запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
