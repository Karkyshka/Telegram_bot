import os
import time

import requests
import telegram
from dotenv import load_dotenv
from telegram import Bot

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
    if (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID) in globals():
        return True
    return False


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(timestamp):
    """Делаем запрос к эндпоинту API-сервиса."""
    timestamp = {'from_date': 1679418196}
    homework_statuses = requests.get(ENDPOINT,
                                     headers=HEADERS,
                                     params=timestamp)
    return homework_statuses.json()


def check_response(response):
    """Проверяем ответ API на соответствие документации."""
    if 'homeworks' not in response:
        raise KeyError('Отсутствует ожидаемый ключ в ответе API')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекаем статус домашней работы."""
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            response = check_response(response)
            if response:
                message = parse_status(response[0])
            else:
                message = 'У вас пока нет домашних заданий на проверке!'
            send_message(bot, message)
            time.sleep(RETRY_PERIOD)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'


if __name__ == '__main__':
    main()
