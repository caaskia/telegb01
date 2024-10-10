import os
import time
import toml
import multiprocessing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json
import redis

import logging
logging.getLogger("watchdog.observers.inotify_buffer").setLevel(logging.ERROR)
logging.basicConfig(level=logging.DEBUG, format="%(module)s - %(message)s")
logging.debug("cam_watch01_2024-04-12_v.0.0.3")


class FileHandler(FileSystemEventHandler):

    def __init__(self, wav_list, redis_client):
        super().__init__()
        self.wav_list = wav_list
        self.redis_client = redis_client

    def on_created(self, event):
        if event.is_directory:
            return
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        msg = f"{now} - Сработка с камеры: {event.src_path}"
        logging.warning(msg)

        img = event.src_path

        # Prepare message data
        message_data = {
            'message': msg,
            'image': img
        }

        # Publish message to Redis channel
        self.redis_client.publish('telegram_messages', json.dumps(message_data))


def monitor_directory(dir_watch, wav_path, redis_client):
    event_handler = FileHandler(wav_path, redis_client)
    observer = Observer()
    observer.schedule(event_handler, path=dir_watch, recursive=False)

    try:
        observer.start()
        logging.info(f"Watching directory: {dir_watch}")

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
        logging.error(f"No config loaded from {path_config}")
        exit(1)

    # Connect to Redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    processes = []

    for key, values in config.items():
        process = multiprocessing.Process(target=monitor_directory,
                                          args=(values['dir'], values['wav'],
                                                redis_client))
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

