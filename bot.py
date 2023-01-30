import asyncio
import aiogram
from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.utils.exceptions import MessageNotModified

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
    text = await Parser().runner()
    with open("standard.gif", 'rb') as gif_file:
        msg = await bot.send_animation(
            TG_CHAT,
            gif_file,
            caption=text
        )
        logging.info("Send first message")
        scheduler.add_job(update_currency, "interval", seconds=15, kwargs={"message": msg})


async def update_currency(message: Message):
    new_message = await Parser().runner()
    try:
        await message.edit_caption(new_message)
        logging.info("Text has be changed")
    except MessageNotModified:
        logging.info("The same text")


if __name__ == '__main__':
    scheduler.start()
    aiogram.executor.start_polling(dp, on_startup=main)
