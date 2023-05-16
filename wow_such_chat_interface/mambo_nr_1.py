import docker
import os
import asyncio
import aiogram
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Command
load_dotenv()

API_KEY = os.getenv('API_KEY')
ADDRESS = os.getenv('ADDRESS')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')


client = docker.from_env()
bot = aiogram.Bot(TELEGRAM_TOKEN)
dp = aiogram.Dispatcher(bot, storage=MemoryStorage())

@dp.message_handler(commands=['status'])
async def handle_status(message: aiogram.types.Message):
    # Retrieve and format the status of all Docker containers
    containers = client.containers.list(all=True)
    status_message = "\n".join([f"{container.name}: {container.status}" for container in containers])

    # Send the status message
    if status_message == '':
        await bot.send_message(chat_id=CHAT_ID, text='No bots running')
    else:
        await bot.send_message(chat_id=CHAT_ID, text=status_message)


class Form(StatesGroup):
    name = State()  # Will be used to collect user's container name
    address = State()  # Will be used to collect user's address
    method = State()  # Will be used to collect user's search method

@dp.message_handler(commands='start')
async def start(message: types.Message):
    await bot.send_message(chat_id=CHAT_ID, text='Bot name:')
    await Form.name.set()

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text.replace(' ', '_')
    await bot.send_message(chat_id=CHAT_ID, text='Address:')
    await Form.next()

@dp.message_handler(state=Form.address)
async def process_address(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['address'] = message.text
    await bot.send_message(chat_id=CHAT_ID, text='Method:\nadd liquidity | create token')
    await Form.next()

@dp.message_handler(state=Form.method)
async def process_method(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['method'] = message.text.lower()

    await bot.send_message(chat_id=CHAT_ID, text='Please wait...')

    env_vars = {}

    if data['method'] == 'add liquidity':
        env_vars['METHOD_ID'] = '0xe8e33700'
    elif data['method'] == 'create token':
        env_vars['METHOD_ID'] = '0xfaa19c2b'

    env_vars['ADDRESS'] = data['address']
    env_vars['BOT_NAME'] = data['name']
    env_vars['TELEGRAM_TOKEN'] = TELEGRAM_TOKEN
    env_vars['CHAT_ID'] = CHAT_ID
    env_vars['API_KEY'] = API_KEY

    # Start a new Docker container with the provided name
    # Replace 'ubuntu' and 'bash' with the image and command you want to use
    container = client.containers.run(image='monitor_bot', name=data['name'], environment=env_vars, detach=True)

    # Send a message indicating that the container has started
    await bot.send_message(chat_id=CHAT_ID, text=f"Started Docker Container {container.id} (name: {data['name']}) at address {data['address']}")
    await state.finish()

if __name__ == '__main__':
    aiogram.executor.start_polling(dp, skip_updates=True)