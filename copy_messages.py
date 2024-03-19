from dotenv import load_dotenv
import os
import time
from pyrogram import Client
from typing import AsyncGenerator
from pyrogram.types import Message
import asyncio

import sqlite3
from contextlib import closing

from services import writing_json, reading_json, get_last_message_id

load_dotenv('.env')  # загружаем данные из виртуального окружения

api_id = os.getenv('TELEGRAM_API_ID')  # получаем api_id, полученный у Telegram
api_hash = os.getenv('TELEGRAM_API_HASH')  # получаем api_hash, полученный у Telegram
username = os.getenv('TELEGRAM_USERNAME')  # получаем имя пользователя для задания имени файла сессии

session_name = f'{username}'  # формируем имя файла сессии Telegram

to_channel_id = os.getenv('GENERAL_CHANNEL_ID')  # ID канала, куда пересылать сообщения


async def get_message_from_channel(from_channel_id, message_id):
    """
    Получаем сообщение из канала по его ID
    :param from_channel_id: ID канала, из которого получаем сообщение
    :param message_id: ID сообщения
    :return:
    """

    # создаем клиент
    client = Client(name=session_name, api_id=api_id, api_hash=api_hash)

    # запускаем клиент
    await client.start()

    message = await client.get_messages(from_channel_id, message_id)
    print(message)

    await client.stop()


async def revers_messages(messages: AsyncGenerator):
    """
    Переворачивает список сообщений, чтобы они шли в правильном порядке
    :param messages: список сообщений
    :return: список сообщений в обратном порядке
    """
    reversed_messages = [message async for message in messages]
    return reversed_messages[::-1]


async def copy_content(from_channel_id: int, channel_tags: str, messages_number=1):
    """
    Получение сообщений из одного канала и пересылка их в другой канал
    :param channel_tags: хэштеги канала
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

    # # записываем данные канала в словарь
    # channel_last_message = {str(from_channel_id): last_message_id}

    # пересылаем сообщения в общий канал
    for message in reversed_messages:

        # await message.copy(chat_id=to_channel_id)
        # print(message)

        # проверяем наличие фото
        if message.photo:
            photo = await message.download(in_memory=True)  # скачиваем фото

            # отправляем фото и сообщение в общий канал
            await client.send_photo(chat_id=to_channel_id, photo=photo, caption='')

            text = message.caption  # получаем текст сообщения

            new_text = f"{channel_tags}\n\n" + text  # добавляем хэштеги в начало сообщения

            await client.send_message(chat_id=to_channel_id, text=new_text)

            time.sleep(1)

        # проверяем наличие видео
        if message.video:
            video = await message.download(in_memory=True)  # скачиваем видео

            # отправляем видео и сообщение в общий канал
            await client.send_video(chat_id=to_channel_id, video=video, caption='')

            text = message.caption  # получаем текст сообщения

            new_text = f"{channel_tags}\n\n" + text  # добавляем хэштеги в начало сообщения

            await client.send_message(chat_id=to_channel_id, text=new_text)

            time.sleep(1)

        # проверяем наличие пересланного сообщения
        if message.forward_from_chat:
            from_chat_id = message.forward_from_chat.id
            # print(from_chat_id)
            # await client.send_message(chat_id=to_channel_id, text=text)

            time.sleep(1)

        # проверяем наличие текста сообщения с кнопками
        if message.text and message.reply_markup:

            text = message.text  # получаем текст сообщения

            new_text = f"{channel_tags}\n\n" + text  # добавляем хэштеги в начало сообщения

            buttons = message.reply_markup.inline_keyboard  # получаем кнопки

            for button in buttons:

                text_button = button[0].text  # текст кнопки
                url_button = button[0].url  # ссылка кнопки

                new_text += f'\n\n{text_button}\n{url_button}'  # добавляем содержимое кнопки к тексту сообщения

            await client.send_message(chat_id=to_channel_id, text=new_text)  # отправляем сообщение в общий канал

            time.sleep(1)
            continue

        # проверяем наличие текста сообщения
        if message.text:

            text = message.text  # получаем текст сообщения

            new_text = f"{channel_tags}\n\n" + text  # добавляем хэштеги в начало сообщения

            await client.send_message(chat_id=to_channel_id, text=new_text)

            time.sleep(1)

        time.sleep(1)

        # # Устанавливаем соединение с базой данных
        connection = sqlite3.connect('channels_database.db', timeout=10)

        cursor = connection.cursor()  # создаем курсор

        # обновляем данные о последнем скопированном сообщении в БД
        cursor.execute('UPDATE Channels SET last_message_id = ? WHERE channel_id = ?',
                       (message.id, from_channel_id))

        connection.commit()  # сохраняем изменения в БД

        connection.close()

    await client.stop()

    return last_message_id


def start_copying():
    """ Запуск пересылки сообщений """

    # Устанавливаем соединение с базой данных
    connection = sqlite3.connect('channels_database.db', timeout=10)

    cursor = connection.cursor()  # создаем курсор

    cursor.execute('SELECT * FROM Channels')  # получаем данные о каналах из БД
    channels_list = cursor.fetchall()  # получаем список каналов

    connection.close()

    # print(channels_list)

    # перебираем каналы из списка
    for channel in channels_list:
        print('Перебираю каналы')
        print(channel)

        channel_id = int(channel[2])  # ID канала
        last_copied_message_id = channel[3]  # ID последнего скопированного сообщения
        channel_tags = channel[4]  # хэштеги канала

        print('Получаю последнее сообщение')
        # получаем ID последнего сообщения из канала в данный момент
        last_message_id = asyncio.run(get_last_message_id(channel_id))
        print(last_message_id)

        # получаем количество сообщений, которые необходимо переслать
        messages_number = last_message_id - last_copied_message_id
        print(messages_number)

        # проверяем есть ли не переправленные сообщения
        if messages_number > 0:
            print('Начал копировать')

            # запускаем копирование сообщений
            channel_last_message = asyncio.run(copy_content(from_channel_id=channel_id,
                                                            channel_tags=channel_tags,
                                                            messages_number=messages_number
                                                            ))
            print('Скопировал')

        else:
            print('Новых сообщений нет')

        time.sleep(2)

    # connection.close()


if __name__ == '__main__':

    # запуск пересылки последних сообщений в общий канал
    # пересылаться будут сообщения, которые еще не пересылались
    # если новых сообщений нет, в терминал выводится сообщение
    def start_program():
        while True:
            try:
                print('Запускаю')
                start_copying()
            except Exception as e:
                print(e)

                time.sleep(30)
                continue
            print('------ Жду ------')
            time.sleep(60)

    start_program()
    # start_copying()
    # a = asyncio.run(get_message_from_channel(-1001369541919, 6725))
