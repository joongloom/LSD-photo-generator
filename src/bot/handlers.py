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
    await state.update_data(intensity="medium", style="trip")
    await message.answer(
        "1) выбери тип эффектов\n"
        "2) выбери нтенсивность\n"
        "3) пришлифото",
        reply_markup=get_settings_kb()
    )


@router.message(F.text.contains("Art"))
async def set_style_art(message: types.Message, state: FSMContext):
    await state.update_data(style="art")
    await message.answer("текстуры и штрихи")


@router.message(F.text.contains("Trip"))
async def set_style_trip(message: types.Message, state: FSMContext):
    await state.update_data(style="trip")
    await message.answer("узоры и формы")


@router.message(F.text.contains("Deep"))
async def set_style_deep(message: types.Message, state: FSMContext):
    await state.update_data(style="deep")
    await message.answer("глаза и галлюцинации")


@router.message(F.text.startswith(("Low", "Medium", "High")))
async def set_intensity(message: types.Message, state: FSMContext):
    intensity = message.text.split()[0].lower()
    await state.update_data(intensity=intensity)
    await message.answer(f"интенсивность: {intensity.capitalize()}")


@router.message(F.photo)
async def handle_photo(message: types.Message, state: FSMContext, processor):
    data = await state.get_data()
    intensity = data.get("intensity", "medium")
    style = data.get("style", "trip")

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    photo_id = message.photo[-1].file_id
    input_path = data_dir / f"in_{photo_id}.jpg"
    output_path = data_dir / f"out_{photo_id}.jpg"

    status = await message.answer(f"обработка...")

    try:
        await message.bot.download(message.photo[-1], destination=str(input_path))
        
        await asyncio.to_thread(
            processor.run_dream, 
            str(input_path), 
            str(output_path), 
            intensity, 
            style
        )

        await message.answer_photo(
            photo=types.FSInputFile(str(output_path))
        )
    except Exception as e:
        logging.error(f"error processing image: {e}")
        await message.answer("произошла ошибка при обработке")
    finally:
        if input_path.exists(): input_path.unlink()
        if output_path.exists(): output_path.unlink()
        await status.delete()