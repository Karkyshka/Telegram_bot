from http import HTTPStatus
import os
import time

import requests
import telegram
from dotenv import load_dotenv
import logging
# import exception

load_dotenv()


PRACTICUM_TOKEN = os.getenv('MY_PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('MY_TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('MY_TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяем доступность переменных окружения."""
    if (PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID) in globals():
        return True
    else:
        logging.critical('Отсутвуют переменные')
        raise KeyError('Отсутвуют переменные')


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    try:
        logging.debug('Статус отправлен в telegram')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.TelegramError:
        logging.error('Сбой при отправке сообщения в Telegram')


def get_api_answer(timestamp):
    """Делаем запрос к эндпоинту API-сервиса."""
    timestamp = {'from_date': timestamp}
    homework_statuses = requests.get(ENDPOINT,
                                     headers=HEADERS,
                                     params=timestamp)
    if requests.RequestException:
        raise ConnectionError
    if homework_statuses.status_code != HTTPStatus.OK:
        logging.error('Ping не проодит')
        raise ConnectionError
    return homework_statuses.json()


def check_response(response):
    """Проверяем ответ API на соответствие документации."""
    if type(response) is not dict:
        raise TypeError('API не соответствует ожиданиям')
    if 'homeworks' not in response:
        logging.error('Отсутсвие ключей')
        raise KeyError('Отсутствует ожидаемый ключ в ответе API')
    if type(response.get('homeworks')) is not list:
        raise TypeError('API не соответствует ожиданиям')
    return response.get('homeworks')


def parse_status(homework):
    """Извлекаем статус домашней работы."""
    try:
        homework_name = homework['homework_name']
        verdict = HOMEWORK_VERDICTS[homework['status']]
    except KeyError:
        # logging.error('Обращение происходит по несуществующему ключу')
        raise KeyError('Неверный статус или ключ')
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
