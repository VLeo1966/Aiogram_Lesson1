import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
import random
import requests
from datetime import datetime, timedelta
from config2 import TOKEN, NASA_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Напиши команду /random_apod, и я пришлю тебе фото.")


def get_random_apod():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    random_date = start_date + (end_date - start_date) * random.random()
    date_str = random_date.strftime("%Y-%m-%d")
    url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}'
    response = requests.get(url)
    return response.json()


@dp.message(Command("random_apod"))
async def random_apod(message: Message):
   apod = get_random_apod()

   # Проверяем, содержит ли ответ ключ 'url' для изображения
   if 'url' in apod and apod['media_type'] == 'image':
      photo_url = apod['url']
      title = apod['title']
      await message.answer_photo(photo=photo_url, caption=f"{title}")
   elif 'url' in apod and apod['media_type'] == 'video':
      video_url = apod['url']
      title = apod['title']
      await message.answer(f"{title}\nЭто видео: {video_url}")
   else:
      # Если ни видео, ни фото нет, сообщаем об ошибке
      await message.answer("Не удалось получить изображение или видео на сегодня. Попробуйте снова позже.")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
