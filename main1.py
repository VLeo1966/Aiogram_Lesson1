import requests
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, FSInputFile, CallbackQuery
import sys

from config import TOKEN, TOKEN2

import random
from gtts import gTTS
import os

import keyboards as kb

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.callback_query(F.data == 'news')
async def news(callback: CallbackQuery):
   await callback.answer("Новости подгружаются", show_alert=True)
   await callback.message.edit_text('Вот свежие новости!', reply_markup=await kb.test2_keyboard())
@dp.message(F.text == "Тестовая кнопка 1")
async def test_button(message: Message):
   await message.answer('Обработка нажатия на reply кнопку1')

@dp.message(F.text == "Тестовая кнопка 2")
async def test_button(message: Message):
   await message.answer('Обработка нажатия на reply кнопку2')

@dp.message(F.text == "Тестовая кнопка 3")
async def test_button(message: Message):
   await message.answer('Обработка нажатия на reply кнопку3')
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Приветики, {message.from_user.first_name}', reply_markup=kb.inline_keyboard_test)

@dp.message(Command('video'))
async def video(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_video")
    video = FSInputFile('video.mp4')
    await bot.send_video(message.chat.id, video)

@dp.message(Command('voice'))
async def voice(message: Message):
    voice = FSInputFile("sample.ogg")
    await message.answer_voice(voice)

@dp.message(Command('doc'))
async def doc(message: Message):
    doc = FSInputFile("TG02.pdf")
    await bot.send_document(message.chat.id, doc)

@dp.message(Command('audio'))
async def audio(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_audio")
    audio = FSInputFile('audio.mp3')
    await bot.send_audio(message.chat.id, audio)


@dp.message(Command('training'))
async def training(message: Message):
   training_list = [
       "Тренировка 1:\n1. Скручивания: 3 подхода по 15 повторений\n2. Велосипед: 3 подхода по 20 повторений (каждая сторона)\n3. Планка: 3 подхода по 30 секунд",
       "Тренировка 2:\n1. Подъемы ног: 3 подхода по 15 повторений\n2. Русский твист: 3 подхода по 20 повторений (каждая сторона)\n3. Планка с поднятой ногой: 3 подхода по 20 секунд (каждая нога)",
       "Тренировка 3:\n1. Скручивания с поднятыми ногами: 3 подхода по 15 повторений\n2. Горизонтальные ножницы: 3 подхода по 20 повторений\n3. Боковая планка: 3 подхода по 20 секунд (каждая сторона)"
   ]
   rand_tr = random.choice(training_list)
   await message.answer(f"Это ваша мини-тренировка на сегодня {rand_tr}")

   tts = gTTS(text=rand_tr, lang='ru')
   tts.save("training.ogg")
   await bot.send_chat_action(message.chat.id, "upload_audio")
   audio = FSInputFile('training.ogg')
   await bot.send_voice(message.chat.id, audio)
   os.remove("training.ogg")

@dp.message(Command('photo', prefix='&'))
async def photo(message: Message):
        list = ['https://avatars.mds.yandex.net/i?id=1cf04a6f38f0be15415a0c35010d27a3c5e70e21-4318341-images-thumbs&n=13',
                'https://avatars.mds.yandex.net/i?id=2414e1a11e8ea018c07319af1c31604f93fa0baa-10165663-images-thumbs&n=13',
                'https://avatars.mds.yandex.net/i?id=423098ad090e0ab751f1ebeef408125a473db425-9283819-images-thumbs&n=13',
                'https://avatars.mds.yandex.net/i?id=a8ffc42530d11d373e07ff512a9e4a96a6562d79-12731000-images-thumbs&n=13']
        rand_photo = random.choice(list)
        await message.answer_photo(photo=rand_photo, caption='Это супер крутая картинка')

@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)
    await bot.download(message.photo[-1], destination=f'tmp/{message.photo[-1].file_id}.jpg')
@dp.message(F.text == "Что такое ИИ?")
async def aitext(message: Message):
    await message.answer('Искусственный интеллект — это свойство искусственных интеллектуальных систем выполнять творческие функции, которые традиционно считаются прерогативой человека; наука и технология создания интеллектуальных машин, особенно интеллектуальных компьютерных программ')

@dp.message(Command('help'))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: \n /start \n /help \n /weather Москва")



# Определение состояний
class WeatherState(StatesGroup):
    waiting_for_city = State()

# Функция для получения погоды
def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={TOKEN2}&units=metric&lang=ru"
    response = requests.get(url)

    # Проверка на успешный запрос
    if response.status_code == 200:
        data = response.json()
        city_name = data['name']
        weather_description = data['weather'][0]['description']
        temperature = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        return f"🏙 Город: {city_name}\n🌡 Температура: {temperature}°C\n☁ Описание: {weather_description.capitalize()}\n💧 Влажность: {humidity}%\n💨 Скорость ветра: {wind_speed} м/с"
    else:
        return "Не удалось получить данные о погоде. Проверьте название города."


# Обработчик команды /weather
@dp.message(Command("weather"))
async def weather_command(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, укажите название города.")
    await state.set_state(WeatherState.waiting_for_city)  # Устанавливаем состояние ожидания города

# Обработчик ввода названия города
@dp.message(WeatherState.waiting_for_city)
async def process_city_input(message: Message, state: FSMContext):
    city = message.text
    weather_info = get_weather(city)
    await message.answer(weather_info)
    await state.clear()  # Сбрасываем состояние после получения прогноза


@dp.message()
async def start(message: Message):
    if message.text.lower() == 'test':
        await message.answer('Тестируем')
'''
@dp.message()
async def start(message: Message):
    await message.send_copy(chat_id=message.chat.id)


@dp.message()
async def start(message: Message):
    await message.answer("Я тебе ответил")
'''

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())