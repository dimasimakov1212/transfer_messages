from dotenv import load_dotenv
import os
import time
from pyrogram import Client
from typing import AsyncGenerator
from pyrogram.types import Message
import asyncio

from services import reading_txt

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

session_name = f'{username}'  # формируем имя файла сессии Telegram

to_channel_id = -1002125329969  # ID канала, куда пересылать сообщения


async def get_channel_id(channel_username):
    """
    Получает ID канала по @username
    :param channel_username: username канала
    :return: ID канала
    """

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # запускаем клиент
    await client.start()

    # получаем ID канала
    channel = await client.get_chat(chat_id=channel_username)
    channel_id = channel.id
    print(channel_id)

    await client.stop()

    return channel_id


if __name__ == '__main__':
    a = asyncio.run(get_channel_id('@bankrollo'))
    # print(a)
