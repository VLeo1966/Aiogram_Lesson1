import requests
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from gtts import gTTS
from googletrans import Translator
import os
import logging
from config import TOKEN

# Инициализация бота с помощью токена
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Включаем логирование для отслеживания ошибок и информации
logging.basicConfig(level=logging.INFO)


# Состояния для команд /translate и /voice, чтобы бот знал, что ждет от пользователя
class TranslateState(StatesGroup):
    waiting_for_text = State()


class VoiceState(StatesGroup):
    waiting_for_text = State()


# Команда /start приветствует пользователя, когда тот запускает бота
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}!')


# Команда /photo - бот предлагает загрузить фото
@dp.message(Command('photo'))
async def photo(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")
    await message.answer_photo('Вставьте фото')


# Обработчик для сохранения фотографий, загружаемых пользователем
@dp.message(F.photo)
async def save_photo(message: Message):
    # Проверка на существование директории для сохранения фото
    if not os.path.exists("img"):
        os.makedirs("img")

    # Скачиваем фото и сохраняем его под уникальным идентификатором
    photo = message.photo[-1]
    file_path = f"img/{photo.file_id}.jpg"
    await bot.download(photo, destination=file_path)

    # Сообщаем пользователю, что фото сохранено
    await message.answer(f"Фото сохранено в {file_path}")


# Команда /translate запрашивает текст для перевода
@dp.message(Command('translate'))
async def text(message: Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, "typing")
    await message.answer('Введите текст, который хотите перевести на английский:')
    await state.set_state(TranslateState.waiting_for_text)  # Ставим бота в состояние ожидания текста для перевода


# Обработчик перевода текста на английский язык
@dp.message(TranslateState.waiting_for_text)
async def translate_text(message: Message, state: FSMContext):
    translator = Translator()
    text_msg = message.text  # Получаем текст сообщения

    # Отправляем индикатор набора текста в чат
    await bot.send_chat_action(message.chat.id, "typing")

    try:
        # Перевод текста с русского на английский с помощью Google Translator
        translated = translator.translate(text=text_msg, dest='en')

        # Отправляем переведенный текст обратно пользователю
        await message.answer(f"Перевод на английский: {translated.text}")
    except Exception as e:
        logging.error(f"Ошибка при переводе: {e}")
        await message.answer("Произошла ошибка при переводе текста.")

    # Сбрасываем состояние после выполнения перевода
    await state.clear()


# Команда /voice просит пользователя ввести текст для преобразования в голос
@dp.message(Command('voice'))
async def voice(message: Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, "record_voice")
    await message.answer('Введите текст, который хотите преобразовать в голосовое сообщение')
    await state.set_state(
        VoiceState.waiting_for_text)  # Ставим бота в состояние ожидания текста для голосового сообщения


# Обработчик текста для создания голосового сообщения
@dp.message(VoiceState.waiting_for_text)
async def send_voice(message: Message, state: FSMContext):
    if not os.path.exists("voice"):
        os.makedirs("voice")

    # Получаем текст сообщения от пользователя
    text_msg = message.text
    await message.answer(f"Преобразуем в голос: {text_msg}")

    # Преобразуем текст в голосовое сообщение с помощью gTTS
    tts = gTTS(text=text_msg, lang='ru')
    tts.save("voice/voice_message.ogg")  # Сохраняем голосовое сообщение в файл

    # Отправляем полученный голосовой файл пользователю
    voice = FSInputFile("voice/voice_message.ogg")
    await bot.send_voice(message.chat.id, voice)

    # Удаляем временный файл с голосом и сбрасываем состояние
    os.remove("voice/voice_message.ogg")
    await state.clear()


# Обработчик текста по умолчанию, если команды /voice или /translate не были активированы
@dp.message(F.text)
async def fallback_text_handler(message: Message):
    await message.answer(
        "Для начала используйте команду /translate для перевода текста или /voice для создания голосового сообщения.")


# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
