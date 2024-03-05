from dotenv import load_dotenv
import os
import time
from pyrogram import Client
import asyncio

from services import reading_txt, preparing_channels, check_id, get_last_message_id, writing_json

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

session_name = f'{username}'  # формируем имя файла сессии Telegram


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

    await client.stop()

    return channel_id


def get_channels():
    """
    Формирует список ID каналов и ID последних сообщений в каналах
    из текстового файла по ссылке на канал или username
    :return:
    """

    # получаем список каналов
    channels_list = reading_txt()

    # преобразуем список для последующего поиска
    channels_list_for_searching = preparing_channels(channels_list)

    # получаем список ID каналов
    id_list = []  # новый список для ID каналов

    for channel in channels_list_for_searching:

        # получаем ID канала
        channel_id = asyncio.run(get_channel_id(channel))

        channel_dict = {channel: channel_id}  # упаковываем в словарь

        id_list.append(channel_dict)  # добавляем в список

        time.sleep(0.2)

    # преобразуем ID для последующего поиска
    id_list_for_searching = []  # новый список для ID каналов

    for channel_dict in id_list:

        for key, volume in channel_dict.items():
            if 'bot' in key.lower():
                id_list_for_searching.append(volume)
            else:
                new_id = check_id(volume)  # проверяем ID
                id_list_for_searching.append(new_id)  # добавляем ID в новый список

    # запускаем поиск последних сообщений в каналах
    channels_with_messages = []  # новый список для каналов и сообщений

    for channel_id in id_list_for_searching:

        # получаем ID последнего сообщения в канале
        last_message_id = asyncio.run(get_last_message_id(channel_id))

        channel = {str(channel_id): last_message_id}  # упаковываем в словарь
        channels_with_messages.append(channel)  # добавляем в список

        time.sleep(0.2)

    # записываем полученные данные о ID каналов и ID последних сообщений в файл
    writing_json(channels_with_messages)


if __name__ == '__main__':

    # Запуск поиска каналов из файла my_channels.txt со списком каналов (ботов, чатов)
    # формируется файл last_messages.json, в котором хранятся данные в виде:
    # ID канала: ID последнего сообщения в канале
    # при последующем запуске пересылки сообщений, берутся сообщения начиная от этих данных
    get_channels()
