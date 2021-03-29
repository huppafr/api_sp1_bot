import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
APPROVED = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
UNAPPROVED = 'К сожалению в работе нашлись ошибки.'
HOMEWORK_CHECKED = 'У вас проверили работу'
BOT_ENCOUNTERED_ERROR = 'Бот столкнулся с ошибкой'


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)


def parse_homework_status(homework):
    """Проверка статуса работы"""
    homework_name = homework.get('homework_name')
    hw_status = homework.get('status')
    if hw_status == 'rejected':
        verdict = UNAPPROVED
    else:
        verdict = APPROVED
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homework_statuses(current_timestamp):
    """Получает статус проверки домашней работы через API."""

    # current_timestamp возвращает текущие дату и время из сеанса пользователя
    # имеет тип данных TIMESTAMP WITH TIME ZONE.
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            URL,
            headers=headers,
            params={'from_date': current_timestamp},
        )
        return homework_statuses.json()
    except Exception as e:
        print(f'{BOT_ENCOUNTERED_ERROR} {e}')


def send_message(message, bot_client):
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())  # начальное значение timestamp

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            if new_homework.get('homeworks'):
                send_message(
                    parse_homework_status(
                        new_homework.get('homeworks')[0]), bot
                )
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )  # обновить timestamp
            time.sleep(300)  # опрашивать раз в пять минут

        except Exception as e:
            print(f'{BOT_ENCOUNTERED_ERROR} {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
