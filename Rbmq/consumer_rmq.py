import json
import pika
from mod_telegram import send_telegram_message, send_telegram_photo

def callback(ch, method, properties, body):
    message_data = json.loads(body.decode())
    msg = message_data.get('message')
    img = message_data.get('image')

    # Send message and photo to Telegram
    send_telegram_message(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, msg)
    send_telegram_photo(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, img)

def consume_messages():
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='telegram_messages')

    channel.basic_consume(queue='telegram_messages', on_message_callback=callback, auto_ack=True)

    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"

    consume_messages()
