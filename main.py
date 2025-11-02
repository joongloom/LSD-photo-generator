import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from src.dream.model import DreamModel
from src.dream.processor import DeepDreamProcessor
from src.bot.handlers import router


async def main():
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    token = os.getenv("BOT_TOKEN")

    os.makedirs("data", exist_ok=True)

    dream_model = DreamModel()
    processor = DeepDreamProcessor(dream_model)

    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    
    logging.info("модель запущена локально")
    
    await dp.start_polling(bot, processor=processor)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("бот остановлен")