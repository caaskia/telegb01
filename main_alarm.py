import os
from dotenv import dotenv_values  # poetry add python-dotenv
import time
import toml
import multiprocessing
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pygame

import asyncio

from mod_telegram import send_telegram_message, send_telegram_photo

import logging
logging.basicConfig(level=logging.DEBUG, format="%(module)s - %(message)s")


class FileHandler(FileSystemEventHandler):

    def __init__(self, wav_list, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID):
        super().__init__()
        self.wav_list = wav_list
        self.TELEGRAM_BOT_TOKEN = TELEGRAM_BOT_TOKEN
        self.TELEGRAM_CHAT_ID = TELEGRAM_CHAT_ID

    async def alarm_telegram(self, msg, img):
        # Call asynchronous functions here with customized message and image
        await send_telegram_message(self.TELEGRAM_BOT_TOKEN, self.TELEGRAM_CHAT_ID, msg)
        await send_telegram_photo(self.TELEGRAM_BOT_TOKEN, self.TELEGRAM_CHAT_ID, img)

    def on_created(self, event):
        if event.is_directory:
            return
        now = time.strftime('%Y-%m-%d %H:%M:%S')

        msg = f"{now} - Сработка с камеры 1: {event.src_path}"
        logging.warning(msg)

        img = event.src_path

        # Run the async method within the event loop
        asyncio.run(self.alarm_telegram(msg, img))

    def alarm_sound(self):
        for wav_path in self.wav_list:
            pygame.mixer.music.load(wav_path)
            pygame.mixer.music.play()
            time.sleep(1.2)


def monitor_directory(dir_watch, wav_path):
    # pygame.init()

    dotenv_path = os.path.expanduser("~/.env")
    env_variables = dotenv_values(dotenv_path)
    TELEGRAM_BOT_TOKEN = env_variables.get("TELEGRAM_BOT_TOKEN")
    TELEGRAM_CHAT_ID = env_variables.get("TELEGRAM_CHAT_ID")

    # Set up the watchdog observer and event handler for each directory
    event_handler = FileHandler(wav_path, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
    observer = Observer()
    observer.schedule(event_handler, path=dir_watch, recursive=False)

    try:
        observer.start()
        print(f"Watching directory: {dir_watch}")

        # Keep the program running
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

    processes = []

    for key, values in config.items():
        process = multiprocessing.Process(target=monitor_directory, args=(values['dir'], values['wav']))
        processes.append(process)
        process.start()

    try:
        # Keep the program running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        # Stop all processes on keyboard interrupt
        for process in processes:
            process.terminate()
            process.join()
    logging.debug("End app")


if __name__ == '__main__':
    main()