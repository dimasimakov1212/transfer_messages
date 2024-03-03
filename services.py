import json

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

# получаем путь к файлу, в котором хранятся каналы
file_last_messages_json = os.path.abspath(f'./last_messages.json')


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


if __name__ == '__main__':
    # asyncio.run(start_search())
    # a = asyncio.run(get_last_message_id(-1001340588812))  # степик
    a = asyncio.run(get_last_message_id(-1001604435961))  # релок
    print(a)
