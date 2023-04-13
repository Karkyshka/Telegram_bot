import logging
import os
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

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
    if all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]):
        return True
    else:
        False


def send_message(bot, message):
    """Отправляем сообщение в Telegram чат."""
    try:
        logging.debug('Статус отправлен в telegram')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as error:
        logging.error('Сбой при отправке сообщения в Telegram')
        raise Exception(f'Сбой при отправке сообщения в Telegram {error}')


def get_api_answer(timestamp):
    """Делаем запрос к эндпоинту API-сервиса."""
    timestamp = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(ENDPOINT,
                                         headers=HEADERS,
                                         params=timestamp)
    except Exception as error:
        raise Exception(f'Ошибка соединения {error}')
    if homework_statuses.status_code != HTTPStatus.OK:
        logging.error('Отсутствие пинга')
        raise ConnectionError('Ошибка соединения')
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
    except Exception as error:
        logging.error('В ключах отсутсвует имя работы или статус')
        raise Exception(f'Неверный статус или ключ {error}')
    if verdict == verdict:
        logging.debug('отсутствие в ответе новых статусов ')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота.
    Проверяем наличие токенов
    Извлекаем статус и текущую дату
    Отправляем сообщение.
    """
    if not check_tokens():
        logging.critical('Отсутствует токен')
        raise SystemExit('Отсутствует токен')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    while True:
        try:
            response = get_api_answer(timestamp)
            timestamp = response.get('current_date')
            homework_statuses = check_response(response)
            if homework_statuses:
                message = parse_status(homework_statuses[0])
            else:
                message = 'У вас пока нет домашних заданий на проверке!'
            send_message(bot, message)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.critical(f'Критическая ошибка {error}')
            raise SystemExit(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
