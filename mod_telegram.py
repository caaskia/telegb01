import logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

import asyncio
from telegram import Bot
from telegram.error import TelegramError


async def send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, message):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")


async def send_telegram_photo(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, path_to_photo):
    try:
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        await bot.send_photo(chat_id=TELEGRAM_CHAT_ID, photo=open(path_to_photo, 'rb'))
    except TelegramError as e:
        print(f"Failed to send Telegram message: {e}")

async def main():
    await send_telegram_message("Передача фото")
    await send_telegram_photo('/home/lynx/Изображения/Таблица.png')



if __name__ == '__main__':
    asyncio.run(main())
