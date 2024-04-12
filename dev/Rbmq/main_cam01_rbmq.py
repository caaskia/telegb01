import os
import time
import toml
import multiprocessing
from dotenv import dotenv_values
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio
import json
import pika  # RabbitMQ

import logging
logging.basicConfig(level=logging.DEBUG, format="%(module)s - %(message)s")

class FileHandler(FileSystemEventHandler):

    def __init__(self, wav_list, rabbitmq_channel):
        super().__init__()
        self.wav_list = wav_list
        self.rabbitmq_channel = rabbitmq_channel

    def on_created(self, event):
        if event.is_directory:
            return
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        msg = f"{now} - Сработка с камеры 1: {event.src_path}"
        logging.warning(msg)

        img = event.src_path

        # Prepare message data
        message_data = {
            'message': msg,
            'image': img
        }

        # Publish message to RabbitMQ
        self.rabbitmq_channel.basic_publish(
            exchange='',
            routing_key='telegram_messages',
            body=json.dumps(message_data)
        )

def monitor_directory(dir_watch, wav_path, rabbitmq_channel):
    event_handler = FileHandler(wav_path, rabbitmq_channel)
    observer = Observer()
    observer.schedule(event_handler, path=dir_watch, recursive=False)

    try:
        observer.start()
        print(f"Watching directory: {dir_watch}")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()

    observer.join()

def main():
    path_config = "./config/alarm.toml"

    with open(path_config, "r") as f:
        config = toml.load(f)

    if not config:
        print(f"No config loaded from {path_config}")
        exit(1)

    # Connect to RabbitMQ
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()
    channel.queue_declare(queue='telegram_messages')

    processes = []

    for key, values in config.items():
        process = multiprocessing.Process(target=monitor_directory, args=(values['dir'], values['wav'], channel))
        processes.append(process)
        process.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        for process in processes:
            process.terminate()
            process.join()
    logging.debug("End app")

if __name__ == '__main__':
    main()
