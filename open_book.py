import asyncio
import requests
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from config3 import TOKEN  # Замените на ваш токен

# Создаем экземпляры бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()


# Функция для поиска книг по названию и получения ссылки на скачивание
def search_books(query):
    url = f"https://openlibrary.org/search.json?q={query}"
    response = requests.get(url)

    # Обрабатываем ответ и возвращаем список книг
    if response.status_code == 200:
        data = response.json()
        books = data.get('docs', [])

        if not books:
            return "Книги не найдены."

        # Формируем текст с результатами
        result = ""
        for book in books[:5]:  # Возвращаем только первые 5 книг
            title = book.get('title', 'Без названия')
            author = book.get('author_name', ['Автор неизвестен'])[0]
            first_publish_year = book.get('first_publish_year', 'Год публикации неизвестен')
            olid = book.get('cover_edition_key')  # Получаем идентификатор книги (OLID)

            # Формируем ссылку на книгу (если есть OLID)
            if olid:
                download_url = f"https://openlibrary.org/books/{olid}/"
                read_online_url = f"https://openlibrary.org/books/{olid}/read"
                result += (f"Название: {title}\n"
                           f"Автор: {author}\n"
                           f"Год публикации: {first_publish_year}\n"
                           f"Читать онлайн: [ссылка]({read_online_url})\n"
                           f"Скачать/Перейти к книге: [ссылка]({download_url})\n\n")
            else:
                result += (f"Название: {title}\n"
                           f"Автор: {author}\n"
                           f"Год публикации: {first_publish_year}\n"
                           f"Ссылка недоступна\n\n")
        return result
    else:
        return "Ошибка при обращении к API Open Library."


# Команда /start
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет! Отправь мне название книги, и я найду её для тебя.")


# Обработка сообщения с запросом книги
@dp.message()
async def handle_message(message: Message):
    query = message.text.strip()

    # Проверка на пустой запрос
    if not query:
        await message.answer("Пожалуйста, введите название книги.")
        return

    # Ищем книги через API Open Library
    await message.answer("Ищу книги, подождите...")
    result = search_books(query)

    # Отправляем пользователю результаты с возможностью скачивания
    await message.answer(result, parse_mode='Markdown')


# Основная функция для запуска бота
async def main():
    await dp.start_polling(bot)


# Точка входа
if __name__ == '__main__':
    asyncio.run(main())
