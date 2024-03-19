import sqlite3

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

    data_list = reading_txt()  # получаем данные из файла со списком каналов

    channels_tags = data_list[0]  # выделяем хэштеги каналов

    channels_list = data_list[1:]  # получаем список каналов

    # преобразуем список для последующего поиска
    channels_list_for_searching = preparing_channels(channels_list)

    # получаем список ID каналов
    channels_dicts_list = []  # новый список для ID каналов

    for channel in channels_list_for_searching:

        # получаем ID канала
        channel_id = asyncio.run(get_channel_id(channel))

        channel_dict = {channel: channel_id}  # упаковываем в словарь

        channels_dicts_list.append(channel_dict)  # добавляем в список

        time.sleep(1)

    # преобразуем ID для последующего поиска
    finish_channels_list = []

    for channel_dict in channels_dicts_list:

        for key, volume in channel_dict.items():
            if 'bot' in key.lower():  # если это бот, то добавляем без изменений
                finish_channels_list.append(channel_dict)
            else:
                new_id = check_id(volume)  # проверяем ID
                channel_dict[key] = new_id
                finish_channels_list.append(channel_dict)  # добавляем ID в новый список

    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('channels_database.db')
    cursor = connection.cursor()  # создаем курсор

    # создаем таблицу с каналами
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Channels (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    channel_id INTEGER NOT NULL,
    last_message_id INTEGER,
    tags TEXT
    )
    ''')

    # перебираем список каналов и заносим в БД
    for channel in finish_channels_list:
        for key, volume in channel.items():

            # получаем ID последнего сообщения в канале
            last_message_id = asyncio.run(get_last_message_id(volume))

            # задаем данные для занесения в БД
            channel_data = (
                key,  # название канала
                volume,  # ID канала
                last_message_id,  # ID последнего сообщения в канале
                channels_tags  # хэштеги канала
            )

            # проверяем существует ли канал в БД
            cursor.execute('SELECT COUNT(*) FROM Channels WHERE channel_id = ?', (volume, ))
            check_channel = cursor.fetchone()[0]

            if check_channel > 0:  # если канал существует, пропускаем его
                pass

            else:  # если канала нет в БД, заносим данные канала в БД
                cursor.execute("""INSERT INTO Channels 
                (name, channel_id, last_message_id, tags) VALUES (?, ?, ?, ?)""",
                               channel_data)

                connection.commit()  # сохраняем изменения в БД

        time.sleep(1)

    connection.close()  # закрываем соединение с БД


def check_bd():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('channels_database.db')
    cursor = connection.cursor()  # создаем курсор

    cursor.execute('SELECT * FROM Channels')
    ch = cursor.fetchall()
    print(ch)

    connection.close()  # закрываем соединение с БД


def change_bd():
    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('channels_database.db')
    cursor = connection.cursor()  # создаем курсор

    cursor.execute('UPDATE Channels SET last_message_id = ? WHERE channel_id = ?',
                   (2756, -1001889919348))
    connection.commit()  # сохраняем изменения в БД
    ch = cursor.fetchall()
    print(ch)

    connection.close()  # закрываем соединение с БД


if __name__ == '__main__':

    # Запуск поиска каналов из файла my_channels.txt со списком каналов (ботов, чатов)
    # формируется файл last_messages.json, в котором хранятся данные в виде:
    # ID канала: ID последнего сообщения в канале
    # при последующем запуске пересылки сообщений, берутся сообщения начиная от этих данных
    # get_channels()
    # check_bd()
    # change_bd()
    check_bd()
