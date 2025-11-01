import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from src.dream.model import DreamModel
from src.dream.processor import DeepDreamProcessor
from src.bot.handlers import router

async def main():
    load_dotenv()
    # Настраиваем логи
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    os.makedirs("data", exist_ok=True)

    # Инициализация ML
    model = DreamModel()
    processor = DeepDreamProcessor(model)

    bot = Bot(token=os.getenv("BOT_TOKEN"))
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("DeepDream Bot запущен!")
    await dp.start_polling(bot, processor=processor)

if __name__ == "__main__":
    asyncio.run(main())