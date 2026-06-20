"""
handlers/who_we_are.py — обработчики раздела «Кто мы?».
Каждый подраздел — отдельный callback-обработчик.
"""

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile

from keyboards.who_we_are_kb import who_we_are_keyboard
from keyboards.back_kb import inline_back_keyboard
from texts.messages import (
    WHO_WE_ARE_INTRO,
    OUR_MISSION,
    WHAT_WE_DO,
    FAQ,
    SOCIAL_NETWORKS,
    PHOTOS_CAPTION,
    NO_PHOTOS,
)

router = Router(name="who_we_are")

# Путь к папке с изображениями (относительно корня проекта)
IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "images")


@router.message(F.text == "👥 Кто мы?")
async def who_we_are_menu(message: Message) -> None:
    """
    Открывает подменю раздела «Кто мы?».
    Если в папке images/ есть файл who_we_are.jpg/png/webp — отправляет его с текстом.
    """
    # Ищем фото раздела (поддерживаются jpg, png, webp)
    photo_path = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        candidate = os.path.join(IMAGES_DIR, f"who_we_are.{ext}")
        if os.path.exists(candidate):
            photo_path = candidate
            break

    if photo_path:
        # Отправляем фото с текстом в подписи
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=WHO_WE_ARE_INTRO,
            reply_markup=who_we_are_keyboard(),
            parse_mode="HTML",
        )
    else:
        # Фото нет — только текст
        await message.answer(
            text=WHO_WE_ARE_INTRO,
            reply_markup=who_we_are_keyboard(),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "wwa:about")
async def about_us(callback: CallbackQuery) -> None:
    """Раздел «О нас»."""
    await callback.message.edit_text(
        text=WHO_WE_ARE_INTRO,
        reply_markup=inline_back_keyboard("wwa:back"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "wwa:mission")
async def our_mission(callback: CallbackQuery) -> None:
    """Раздел «Наша миссия»."""
    await callback.message.edit_text(
        text=OUR_MISSION,
        reply_markup=inline_back_keyboard("wwa:back"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "wwa:what_we_do")
async def what_we_do(callback: CallbackQuery) -> None:
    """Раздел «Чем мы занимаемся»."""
    await callback.message.edit_text(
        text=WHAT_WE_DO,
        reply_markup=inline_back_keyboard("wwa:back"),
        parse_mode="HTML",
    )
    await callback.answer()



@router.callback_query(F.data == "wwa:faq")
async def faq(callback: CallbackQuery) -> None:
    """Раздел «FAQ»."""
    await callback.message.edit_text(
        text=FAQ,
        reply_markup=inline_back_keyboard("wwa:back"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "wwa:social")
async def social_networks(callback: CallbackQuery) -> None:
    """Раздел «Наши социальные сети»."""
    await callback.message.edit_text(
        text=SOCIAL_NETWORKS,
        reply_markup=inline_back_keyboard("wwa:back"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "wwa:photos")
async def photos(callback: CallbackQuery) -> None:
    """
    Раздел «Фото и видео».
    Отправляет все изображения из папки images/.
    Чтобы добавить фото — просто положи файл в папку images/.
    """
    await callback.answer()

    # Собираем список фото из папки images/
    image_files = [
        f for f in os.listdir(IMAGES_DIR)
        if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ] if os.path.isdir(IMAGES_DIR) else []

    if not image_files:
        # Фотографий пока нет — показываем заглушку
        await callback.message.edit_text(
            text=NO_PHOTOS,
            reply_markup=inline_back_keyboard("wwa:back"),
            parse_mode="HTML",
        )
        return

    # Отправляем каждое фото
    await callback.message.answer(text=PHOTOS_CAPTION, parse_mode="HTML")
    for image_file in image_files:
        image_path = os.path.join(IMAGES_DIR, image_file)
        await callback.message.answer_photo(
            photo=FSInputFile(image_path),
        )


@router.callback_query(F.data == "wwa:back")
async def back_to_who_we_are(callback: CallbackQuery) -> None:
    """Возврат в подменю «Кто мы?»."""
    await callback.message.edit_text(
        text=WHO_WE_ARE_INTRO,
        reply_markup=who_we_are_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()
