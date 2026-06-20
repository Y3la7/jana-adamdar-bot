"""
handlers/who_we_are.py — обработчики раздела «Кто мы?».
Каждый подраздел — отдельный callback-обработчик.
"""

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, FSInputFile, InlineKeyboardMarkup

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


async def show_text(callback: CallbackQuery, text: str, reply_markup: InlineKeyboardMarkup) -> None:
    """
    Вспомогательная функция: если исходное сообщение — фото,
    удаляем его и отправляем новое текстовое. Иначе — просто редактируем.
    """
    if callback.message.photo:
        await callback.message.delete()
        await callback.message.answer(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )
    else:
        await callback.message.edit_text(
            text=text,
            reply_markup=reply_markup,
            parse_mode="HTML",
        )


@router.message(F.text == "👥 Кто мы?")
async def who_we_are_menu(message: Message) -> None:
    """
    Открывает подменю раздела «Кто мы?».
    Если в папке images/ есть файл who_we_are.jpg/png/webp — отправляет его с текстом.
    """
    photo_path = None
    for ext in ("jpg", "jpeg", "png", "webp"):
        candidate = os.path.join(IMAGES_DIR, f"who_we_are.{ext}")
        if os.path.exists(candidate):
            photo_path = candidate
            break

    if photo_path:
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=WHO_WE_ARE_INTRO,
            reply_markup=who_we_are_keyboard(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            text=WHO_WE_ARE_INTRO,
            reply_markup=who_we_are_keyboard(),
            parse_mode="HTML",
        )


@router.callback_query(F.data == "wwa:about")
async def about_us(callback: CallbackQuery) -> None:
    """Раздел «О нас»."""
    await show_text(callback, WHO_WE_ARE_INTRO, inline_back_keyboard("wwa:back"))
    await callback.answer()


@router.callback_query(F.data == "wwa:mission")
async def our_mission(callback: CallbackQuery) -> None:
    """Раздел «Наша миссия»."""
    await show_text(callback, OUR_MISSION, inline_back_keyboard("wwa:back"))
    await callback.answer()


@router.callback_query(F.data == "wwa:what_we_do")
async def what_we_do(callback: CallbackQuery) -> None:
    """Раздел «Чем мы занимаемся»."""
    await show_text(callback, WHAT_WE_DO, inline_back_keyboard("wwa:back"))
    await callback.answer()


@router.callback_query(F.data == "wwa:faq")
async def faq(callback: CallbackQuery) -> None:
    """Раздел «FAQ»."""
    await show_text(callback, FAQ, inline_back_keyboard("wwa:back"))
    await callback.answer()


@router.callback_query(F.data == "wwa:social")
async def social_networks(callback: CallbackQuery) -> None:
    """Раздел «Наши социальные сети»."""
    await show_text(callback, SOCIAL_NETWORKS, inline_back_keyboard("wwa:back"))
    await callback.answer()


@router.callback_query(F.data == "wwa:photos")
async def photos(callback: CallbackQuery) -> None:
    """
    Раздел «Фото и видео».
    Отправляет все gallery_*.jpg изображения из папки images/.
    """
    await callback.answer()

    gallery_files = sorted([
        f for f in os.listdir(IMAGES_DIR)
        if f.startswith("gallery_") and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))
    ]) if os.path.isdir(IMAGES_DIR) else []

    if not gallery_files:
        await show_text(callback, NO_PHOTOS, inline_back_keyboard("wwa:back"))
        return

    # Удаляем исходное сообщение если это фото
    if callback.message.photo:
        await callback.message.delete()

    await callback.message.answer(text=PHOTOS_CAPTION, parse_mode="HTML")
    for image_file in gallery_files:
        image_path = os.path.join(IMAGES_DIR, image_file)
        await callback.message.answer_photo(photo=FSInputFile(image_path))


@router.callback_query(F.data == "wwa:back")
async def back_to_who_we_are(callback: CallbackQuery) -> None:
    """Возврат в подменю «Кто мы?»."""
    await show_text(callback, WHO_WE_ARE_INTRO, who_we_are_keyboard())
    await callback.answer()
