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

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Определение состояний для перевода и создания голосового сообщения
class TranslateState(StatesGroup):
    waiting_for_text = State()

class VoiceState(StatesGroup):
    waiting_for_text = State()

# Определение состояний для обработки текста и создания голосового сообщения
class VoiceState(StatesGroup):
    waiting_for_text = State()

# Команда /start
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(f'Привет, {message.from_user.first_name}!')

# Команда /photo
@dp.message(Command('photo'))
async def photo(message: Message):
    await bot.send_chat_action(message.chat.id, "upload_photo")
    await message.answer_photo('Вставьте фото')

# Сохранение фото в папке img
@dp.message(F.photo)
async def save_photo(message: Message):
    if not os.path.exists("img"):
        os.makedirs("img")
    photo = message.photo[-1]
    file_path = f"img/{photo.file_id}.jpg"
    await bot.download(photo, destination=file_path)
    await message.answer(f"Фото сохранено в {file_path}")



# Команда для начала перевода текста на английский
@dp.message(Command('translate'))
async def text(message: Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, "typing")
    await message.answer('Введите текст, который хотите перевести на английский:')
    await state.set_state(TranslateState.waiting_for_text)  # Устанавливаем состояние ожидания текста для перевода

# Перевод текста пользователя на английский язык
@dp.message(TranslateState.waiting_for_text)
async def translate_text(message: Message, state: FSMContext):
    translator = Translator()
    text_msg = message.text  # Получаем текст сообщения
    await bot.send_chat_action(message.chat.id, "typing")  # Указываем "typing" для процесса перевода

    try:
        # Перевод текста с помощью googletrans
        translated = translator.translate(text=text_msg, dest='en')
        # Отправка переведенного текста
        await message.answer(f"Перевод на английский: {translated.text}")
    except Exception as e:
        logging.error(f"Ошибка при переводе: {e}")
        await message.answer("Произошла ошибка при переводе текста.")

    await state.clear()  # Сбрасываем состояние после перевода

# Команда для создания голосового сообщения
@dp.message(Command('voice'))
async def voice(message: Message, state: FSMContext):
    await bot.send_chat_action(message.chat.id, "record_voice")
    await message.answer('Введите текст, который хотите преобразовать в голосовое сообщение')
    await state.set_state(VoiceState.waiting_for_text)  # Устанавливаем состояние ожидания текста для голосового сообщения

# Обработка текста для создания голосового сообщения
@dp.message(VoiceState.waiting_for_text)
async def send_voice(message: Message, state: FSMContext):
    if not os.path.exists("voice"):
        os.makedirs("voice")
    text_msg = message.text  # Получаем текст сообщения
    await message.answer(f"Преобразуем в голос: {text_msg}")

    # Преобразование текста в голос с помощью gTTS
    tts = gTTS(text=text_msg, lang='ru')
    tts.save("voice/voice_message.ogg")  # Сохраняем временный файл

    # Отправка голосового сообщения
    voice = FSInputFile("voice/voice_message.ogg")
    await bot.send_voice(message.chat.id, voice)

    # Удаление временного файла и сброс состояния
    os.remove("voice/voice_message.ogg")
    await state.clear()

# Если текст поступает без активного состояния, например, команды /voice или /translate
@dp.message(F.text)
async def fallback_text_handler(message: Message):
    await message.answer("Для начала используйте команду /translate для перевода текста или /voice для создания голосового сообщения.")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
