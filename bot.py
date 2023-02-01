import aiogram
from aiogram import Dispatcher
from aiogram.types import Message
from parser import Parser
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
TG_CHAT = os.getenv("TG_CHAT")

bot = aiogram.Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler()


async def main(dp: Dispatcher):
    global msg
    text = await Parser().runner()
    with open("standard.gif", 'rb') as gif_file:
        await bot.send_animation(
            TG_CHAT,
            gif_file,
        )
    msg = await bot.send_message(TG_CHAT, text=text)
    logging.info("Send first message")
    scheduler.add_job(update_currency, "interval", seconds=15)


async def update_currency():
    global msg
    new_text = await Parser().runner()
    try:
        await msg.delete()
        msg = await bot.send_message(TG_CHAT, text=new_text)
        logging.info("Sent new message")
    except Exception as e:
        logging.info(e)


if __name__ == '__main__':
    scheduler.start()
    aiogram.executor.start_polling(dp, on_startup=main)
