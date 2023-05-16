import docker
import os
import asyncio
import aiogram
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv

load_dotenv()

#TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_TOKEN = '6090299176:AAFObU84x3jLxxvMPQbPOXHrtdoZOni0oUM'

client = docker.from_env()
bot = aiogram.Bot(TELEGRAM_TOKEN)
dp = aiogram.Dispatcher(bot)

@dp.message_handler(commands=['status'])
async def handle_status(message: aiogram.types.Message):
    # Retrieve and format the status of all Docker containers
    containers = client.containers.list(all=True)
    status_message = "\n".join([f"{container.name}: {container.status}" for container in containers])

    # Send the status message
    await bot.send_message(chat_id=message.chat.id, text=status_message)

@dp.message_handler(commands=['start'])
async def handle_start(message: aiogram.types.Message):
    env_vars = message.text.split()[1:]  # Get the environment variables
    env_dict = {var.split('=')[0]: var.split('=')[1] for var in env_vars}

    # Start a new Docker container with the provided environment variables
    # Here, I assume that you want to run a container from the 'ubuntu' image
    # Please replace 'ubuntu' and the command with your actual image and command
    container = client.containers.run(image='monitor_bot', environment=env_dict, detach=True)

    # Send a message indicating that the container has started
    await bot.send_message(chat_id=message.chat.id, text=f"Started Docker Container {container.id} with {env_vars}")

if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)