from pprint import pprint

import requests
from telegram import Bot, ReplyKeyboardMarkup

ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
PRACTICUM_TOKEN = 'y0_AgAAAAArM5YXAAYckQAAAADgqKX-ETl3w_GOQiKAGcqGzp6iUEClRPY'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
TELEGRAM_TOKEN = '6126889100:AAFxQZm7JDmeNVyIDYHEhNw6sSUaE9sP6QQ' 
CHAT_ID = '889248'

payload = {'from_date': 1679418196}
bot = Bot(token=TELEGRAM_TOKEN)

homework_statuses = requests.get(ENDPOINT,
                                 headers=HEADERS,
                                 params=payload)


pprint(homework_statuses.json())

# status = homework_statuses.get('status') 
# send_message(bot, homework_statuses.json())