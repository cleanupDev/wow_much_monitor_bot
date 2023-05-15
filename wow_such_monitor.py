import requests
import time
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

load_dotenv()

API_KEY = os.environ['API_KEY']
ADDRESS = os.environ['ADDRESS']

TELEGRAM_TOKEN = os.environ['TELEGRAM_TOKEN']
CHAT_ID = os.environ['CHAT_ID']
BOT_NAME = os.environ['BOT_NAME']

METHOD_ID = '0xfaa19c2b' # Wow Much coin created!

bot = Bot(token=TELEGRAM_TOKEN)

async def get_recent_transactions_with_method_id(address, method_id):
    url = f'https://api.bscscan.com/api?module=account&action=txlist&address={address}&sort=desc&apikey={API_KEY}'
    response = requests.get(url).json()
    
    if response['status'] == '1':
        transactions = response['result']
        # Filter for transactions where the method ID is at the start of the input data
        transactions_with_method_id = [tx for tx in transactions if tx['input'].startswith(method_id)]
        # Get the current time in Unix timestamp format
        current_time = int(time.time())
        # Filter for transactions from the past 5 minutes
        recent_transactions = [tx for tx in transactions_with_method_id if current_time - int(tx['timeStamp']) <= 300]
        return recent_transactions
    else:
        return []

async def monitor_address(address, method_id, interval):
    await bot.send_message(chat_id=CHAT_ID, text=f"🏁🏁🏁\n<b><i><code style='color:red;'>{BOT_NAME}</code></i></b>\nstarted monitoring address\n{address}\nfor transactions with method ID {method_id} \n🏁🏁🏁", parse_mode='HTML')
    while True:
        transactions = await get_recent_transactions_with_method_id(address, method_id)
        if transactions:
            for tx in transactions:
                message = f"🚨🚨🚨 NEW COIN CREATED! 🚨🚨🚨\nRecent transaction with method ID\n{method_id}\n at block {tx['blockNumber']} with hash {tx['hash']}\nLET'S GOOOO 💰💰💰"
                print(message)
                await bot.send_message(chat_id=CHAT_ID, text=message)
        else:
            print(f'{BOT_NAME} found no recent transactions with method ID ----- Time: {time.ctime()}')
        await asyncio.sleep(interval)

asyncio.run(monitor_address(ADDRESS, METHOD_ID, 20))