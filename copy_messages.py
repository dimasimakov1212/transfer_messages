from dotenv import load_dotenv
import os
from pyrogram import Client
from typing import AsyncGenerator
from pyrogram.types import Message
import asyncio

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

session_name = f'{username}'  # формируем имя файла сессии Telegram
# session_name = str(username)


async def revers_messages(messages: AsyncGenerator):
    """

    :param messages:
    :return:
    """
    reversed_messages = [message async for message in messages]
    return reversed_messages[::-1]


async def copy_content(from_channel_id: int, to_channel_id: int):
    """

    :param from_channel_id:
    :param to_channel_id:
    :return:
    """
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)
    await client.start()

    messages: AsyncGenerator[Message, None] = client.get_chat_history(chat_id=from_channel_id,
                                                                      limit=2)

    reversed_messages = await revers_messages(messages=messages)

    for message in reversed_messages:
        print(message)
        await message.copy(chat_id=to_channel_id)

    await client.stop()


asyncio.run(copy_content(from_channel_id=-1001202159807, to_channel_id=-1002125329969))
# asyncio.run(copy_content(from_channel_id=-1001606563124, to_channel_id=-1002125329969))  # skypro чат

