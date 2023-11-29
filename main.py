import asyncio
import logging
from os import getenv

from aiogram.utils.token import validate_token
from dotenv import load_dotenv

from bot import *
from messages import error

load_dotenv()
BOT_TOKEN = getenv("BOT_TOKEN")
DEBUG_MODE = getenv("DEBUG_MODE")
LOG_FILE = getenv("LOG_FILE")


async def main() -> None:
    print('''\033[1;92mTelegram-бот Расписание ОмГТУ\033[0m
Поможет:  > узнать расписание;
|  |  |   > найти преподавателя;
  |  |    > узнать аудиторию.
Отличный помощник для студента и преподавателя в любимом мессенджере.
Сделано в рамках курсового проекта в 2023 году.
\033[3m(с) Роман Корноухов, студент гр. ПИН-222.
\033[5mhttps://github.com/wtxsuper/omgtu-bot\n\033[0m''')
    try:
        if not BOT_TOKEN or BOT_TOKEN == '':
            raise NameError("No token provided")
        if not validate_token(BOT_TOKEN):
            raise NameError("Token Validation Failed")
        if DEBUG_MODE == "1":
            if LOG_FILE:
                logging.basicConfig(filename=LOG_FILE, encoding='utf-8', level=logging.DEBUG)
            else:
                logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=0)
    except:
        error('Ошибка инициализации окружения! Проверьте содержимое файла .env.')
    else:
        logging.debug("Окружение успешно загружено.")
        await bot_start(BOT_TOKEN)


if __name__ == '__main__':
    asyncio.run(main())
