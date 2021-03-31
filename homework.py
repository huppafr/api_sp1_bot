import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv('PRAKTIKUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
URL = 'https://praktikum.yandex.ru/api/user_api/homework_statuses/'
APPROVED = 'Ревьюеру всё понравилось, можно приступать к следующему уроку.'
UNAPPROVED = 'К сожалению в работе нашлись ошибки.'
BOT_ENCOUNTERED_ERROR = 'Бот столкнулся с ошибкой'
STATUS_ERROR = 'Ошибка получения статуса работы'
MY_BOT = telegram.Bot(token=TELEGRAM_TOKEN)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=10
)
logger = logging.getLogger(__name__)


def parse_homework_status(homework):
    """Проверка статуса работы"""
    try:
        homework_name = homework.get('homework_name')
        hw_status = homework.get('status')
        if hw_status == 'reviewing':
            return f'Работа {homework_name} взята на ревью'
        elif hw_status == 'rejected':
            verdict = UNAPPROVED
        else:
            verdict = APPROVED
        return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'
    except Exception as e:
        logger.error(f'{STATUS_ERROR} {e}')
        send_message(f'{STATUS_ERROR} {e}', MY_BOT)


def get_homework_statuses(current_timestamp):
    """Получает статус проверки домашней работы через API."""
    headers = {'Authorization': f'OAuth {PRAKTIKUM_TOKEN}'}
    try:
        homework_statuses = requests.get(
            URL,
            headers=headers,
            params={'from_date': current_timestamp},
        )
        return homework_statuses.json()
    except Exception as e:
        logger.error(f'{BOT_ENCOUNTERED_ERROR} {e}')
        send_message((f'{BOT_ENCOUNTERED_ERROR} {e}'), MY_BOT)


def send_message(message, bot_client):
    logger.info(f'Бот отправил сообщение')
    return bot_client.send_message(chat_id=CHAT_ID, text=message)


def main():
    current_timestamp = int(time.time())  # начальное значение timestamp
    logger.debug(f'Бот начал свою работу')

    while True:
        try:
            new_homework = get_homework_statuses(current_timestamp)
            get_homework = new_homework.get('homeworks')
            if get_homework:
                send_message(
                    parse_homework_status(
                        get_homework[0]), MY_BOT
                )
            current_timestamp = new_homework.get(
                'current_date',
                current_timestamp
            )  # обновить timestamp
            time.sleep(3000)  # опрашивать раз в пять минут

        except Exception as e:
            logger.error(f'{BOT_ENCOUNTERED_ERROR} {e}')
            send_message((f'{BOT_ENCOUNTERED_ERROR} {e}'), MY_BOT)
            time.sleep(5)


if __name__ == '__main__':
    main()
