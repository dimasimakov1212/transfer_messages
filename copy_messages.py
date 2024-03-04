from dotenv import load_dotenv
import os
import time
from pyrogram import Client
from typing import AsyncGenerator
from pyrogram.types import Message
import asyncio

from services import writing_json, reading_json, get_last_message_id

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

session_name = f'{username}'  # формируем имя файла сессии Telegram

to_channel_id = -1002125329969  # ID канала, куда пересылать сообщения


async def revers_messages(messages: AsyncGenerator):
    """
    Переворачивает список сообщений, чтобы они шли в правильном порядке
    :param messages: список сообщений
    :return: список сообщений в обратном порядке
    """
    reversed_messages = [message async for message in messages]
    return reversed_messages[::-1]


async def copy_content(from_channel_id: int, messages_number=1):
    """
    Получение сообщений из одного канала и пересылка их в другой канал
    :param messages_number: количество сообщений для пересылки
    :param from_channel_id: id канала, из которого получаем сообщения
    :return: словарь, где ключ - это ID канала, значение - ID последнего скопированного сообщения
    """

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # запускаем клиент
    await client.start()

    # получаем список сообщений
    messages: AsyncGenerator[Message, None] = client.get_chat_history(chat_id=from_channel_id,
                                                                      limit=messages_number)

    # делаем реверс списка сообщений, чтобы они шли в правильном порядке
    reversed_messages = await revers_messages(messages=messages)

    # получаем id последнего сообщения
    last_message_id = reversed_messages[-1:][0].id

    # записываем данные канала в словарь
    channel_last_message = {str(from_channel_id): last_message_id}

    # пересылаем сообщения в общий канал
    for message in reversed_messages:

        # await message.copy(chat_id=to_channel_id)

        # проверяем наличие текста сообщения
        if message.text:
            text = message.text
            await client.send_message(chat_id=to_channel_id, text=text)

            time.sleep(0.2)

        # проверяем наличие фото
        if message.photo:
            photo = await message.download(in_memory=True)
            await client.send_photo(chat_id=to_channel_id, photo=photo, caption=message.caption)

            time.sleep(0.2)

        # проверяем наличие кнопок
        if message.reply_markup:
            buttons = message.reply_markup.inline_keyboard

            for button in buttons:

                text_button = button[0].text
                url_button = button[0].url

                text = f'{text_button}\n{url_button}'
                await client.send_message(chat_id=to_channel_id, text=text)

                time.sleep(0.2)

        time.sleep(0.4)

    await client.stop()

    return channel_last_message


def start_copying():
    """ Запуск пересылки сообщений """

    # получаем список словарей каналов, где
    # ключ словаря - это ID канала, значение - ID последнего скопированного сообщения
    channels_list = reading_json()

    # новый список каналов
    new_channels_list = []

    # перебираем каналы из списка
    for channel in channels_list:
        for key, value in channel.items():
            channel_id = int(key)  # ID канала
            last_copied_message_id = value  # ID последнего скопированного сообщения

            # получаем ID последнего сообщения из канала
            last_message_id = asyncio.run(get_last_message_id(channel_id))

            # получаем количество сообщений, которые необходимо переслать
            messages_number = last_message_id - last_copied_message_id

            # проверяем есть ли не переправленные сообщения
            if messages_number > 0:

                # запускаем копирование сообщений
                channel_last_message = asyncio.run(copy_content(from_channel_id=channel_id,
                                                                messages_number=messages_number))

                # добавляем данные канала в новый список
                new_channels_list.append(channel_last_message)

            else:
                print('Новых сообщений нет')

            time.sleep(2)

    # записываем обновленные данные о каналах
    writing_json(new_channels_list)


if __name__ == '__main__':
    start_copying()
