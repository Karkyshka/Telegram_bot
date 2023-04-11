import time
import requests
import telegram
from telegram import Bot
from telegram.ext import Updater, Filters, MessageHandler
import os
from dotenv import load_dotenv

load_dotenv()


PRACTICUM_TOKEN = os.getenv('MY_PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('MY_TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяем доступность переменных окружения."""
    if PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        return True
    return False


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(timestamp):
    """Делаем запрос к эндпоинту API-сервиса."""
    timestamp = {'from_date': 0}
    homework_statuses = requests.get(ENDPOINT,
                                     headers=HEADERS,
                                     params=timestamp)
    return homework_statuses.json()


def check_response(response):
    """Проверяем ответ API на соответствие документации."""
    response = requests.get(ENDPOINT).json()
    ...


def parse_status(homework):
    """Извлекаем статус домашней работы."""
    homework = requests.get(ENDPOINT).json()
    homework_name = homework[0].get('homework_name')
    verdict = homework[0].get('status')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            check_response(get_api_answer(timestamp))
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
        


if __name__ == '__main__':
    main()
