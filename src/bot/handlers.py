import asyncio
import logging
from pathlib import Path
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from .keyboards import get_settings_kb

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.update_data(intensity="medium", is_random=False)
    await message.answer(
        "Бот готов! Выбери режим кнопками или просто пришли фото.",
        reply_markup=get_settings_kb()
    )

# Хендлер для выбора интенсивности
@router.message(F.text.in_(["Low", "Medium", "High"]))
async def set_intensity(message: types.Message, state: FSMContext):
    await state.update_data(intensity=message.text.lower(), is_random=False)
    await message.answer(f"✅ Установлен режим: {message.text}")

# Хендлер для рандома
@router.message(F.text == "🎲 Surprise Me (Random)")
async def set_random(message: types.Message, state: FSMContext):
    await state.update_data(is_random=True)
    await message.answer("✅ Режим Random включен! Галлюцинации будут непредсказуемыми.")

@router.message(F.photo)
async def handle_photo(message: types.Message, state: FSMContext, processor):
    data = await state.get_data()
    intensity = data.get("intensity", "medium")
    is_random = data.get("is_random", False)

    # Работа с путями
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    photo = message.photo[-1]
    input_path = data_dir / f"in_{photo.file_id}.jpg"
    output_path = data_dir / f"out_{photo.file_id}.jpg"

    status_msg = await message.answer(f"🧠 Работаю в режиме {intensity.upper()}... Ждите.")

    try:
        # Скачиваем
        await message.bot.download(photo, destination=str(input_path))
        
        # Запускаем DeepDream
        await asyncio.to_thread(
            processor.run_dream, 
            str(input_path), str(output_path), intensity, is_random
        )

        # Отправляем результат
        await message.answer_photo(
            photo=types.FSInputFile(str(output_path)),
            caption=f"Готово! Степень: {intensity}"
        )
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка при обработке нейронкой.")
    finally:
        if input_path.exists(): input_path.unlink()
        if output_path.exists(): output_path.unlink()
        await status_msg.delete()