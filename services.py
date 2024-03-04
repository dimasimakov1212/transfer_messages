import json

import pyrogram
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

# путь к файлу, в котором хранятся ID каналов и ID последних скопированных сообщений
file_last_messages_json = os.path.abspath(f'./last_messages.json')

# путь к файлу, в котором хранятся каналы для поиска
file_channels_txt = os.path.abspath(f'./my_channels.txt')


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
    """ Запуск отслеживания сообщения пользователя в закрытом канале """

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # отслеживаем сообщение в чате
    client.add_handler(MessageHandler(callback=get_channel_id))

    try:
        await client.start()
        await idle()  # ожидаем событие в канале
    except Exception:
        await client.stop()


def writing_json(data_list):
    """ Записывает данные в формате json """

    with open(file_last_messages_json, 'w', encoding='utf-8') as file:
        json.dump(data_list, file, sort_keys=False, indent=4, ensure_ascii=False)


def reading_json():
    """ Считывает данные из формата json """

    try:
        with open(file_last_messages_json, 'r', encoding='utf-8') as file:
            data_list = json.load(file)
        return data_list
    except FileNotFoundError:
        print('Файла пока не существует, будет создан новый файл')
        data_list = []
        return data_list


async def get_last_message_id(channel_id: int):
    """
    Получает ID последнего сообщения в канале
    :param channel_id: ID канала
    :return: ID сообщения
    """

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # запускаем клиент
    await client.start()

    # получаем последнее сообщение
    last_message = client.get_chat_history(chat_id=channel_id, limit=1)

    async for item in last_message:
        last_message_id = item.id
        # print(item)

        await client.stop()

        return last_message_id


def reading_txt():
    """ Считывает построчно данные из файла txt """

    try:
        with open(file_channels_txt, 'r') as file:
            channels = file.read().splitlines()
        return channels
    except FileNotFoundError:
        print('Файла пока не существует, проверьте данные')
        channels = []
        return channels


def preparing_channels(channels_list):
    """
    Подготовка имени канала для поиска
    :param channels_list: список каналов
    :return: список каналов для поиска
    """

    # новый список для каналов
    new_channels_list = []

    for channel in channels_list:
        if 'https://t.me' in channel:
            prepared_name = channel.split('/')[-1:][0]
            new_channels_list.append(prepared_name)

        else:
            new_channels_list.append(channel)

    return new_channels_list


async def searching_channels_by_title(channel_title):
    """
    Поиск ID канала по его названию
    :param channel_title: название канала
    :return: ID канала
    """

    # список для каналов
    channels_list = []

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # запускаем клиент
    await client.start()

    # делаем поиск каналов
    search = await client.invoke(pyrogram.raw.functions.contacts.Search(q=channel_title, limit=3))

    # проверяем список найденных каналов
    for chat in search.chats:

        channel_id = chat.id  # ID канала

        channel = {chat.title: channel_id}  # упаковываем в словарь
        channels_list.append(channel)  # добавляем в список

    await client.stop()

    return channels_list


def check_id(channel_id):
    """
    Проверяет ID канала на соответствие требованиям
    :param channel_id: ID канала
    :return: обновленный ID канала
    """

    # если ID канала составляет 10 символов, добавляем префикс
    if len(str(channel_id)) == 10:
        channel_id = int('-100' + str(channel_id))

    return channel_id


# if __name__ == '__main__':

    # a = asyncio.run(get_last_message_id(-1001989338321))  #
    # print(a)
