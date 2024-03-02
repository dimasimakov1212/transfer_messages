from dotenv import load_dotenv
import os
from pyrogram import Client, idle
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler
import asyncio

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

session_name = f'{username}'  # формируем имя файла сессии Telegram


async def get_channel_id(client: Client, message: Message):
    """
    Получение id канала
    :param client:
    :param message:
    :return:
    """
    print(message)
    print(message.chat.id)


async def start_search():
    """ Запуск отслеживания сообщения пользователя """

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # отслеживаем сообщение в чате
    client.add_handler(MessageHandler(callback=get_channel_id))

    try:
        await client.start()
        await idle()  # ожидаем событие в канале
    except Exception:
        await client.stop()


if __name__ == '__main__':
    asyncio.run(start_search())
