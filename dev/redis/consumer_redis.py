import os
from dotenv import dotenv_values  # poetry add python-dotenv
import json
import redis
from mod_telegram import send_telegram_message, send_telegram_photo

async def process_message(msg, img):
    # Send message and photo to Telegram
    await send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
    await send_telegram_photo(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, img)

async def consume_messages():
    redis_client = redis.Redis(host='localhost', port=6379, db=0)
    pubsub = redis_client.pubsub()
    pubsub.subscribe('telegram_messages')

    for message in pubsub.listen():
        if message['type'] == 'message':
            message_data = json.loads(message['data'].decode())
            msg = message_data.get('message')
            img = message_data.get('image')

            # Ensure proper asynchronous handling
            await process_message(msg, img)

if __name__ == '__main__':

    dotenv_path = os.path.expanduser("~/.env")
    env_variables = dotenv_values(dotenv_path)
    TELEGRAM_BOT_TOKEN = env_variables.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = env_variables.get("TELEGRAM_CHAT_ID")

    # Run the asyncio event loop
    import asyncio
    asyncio.run(consume_messages())
