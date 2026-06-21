"""
handlers/broadcast.py — отслеживание групп и рассылка сообщений.
"""

from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    Message, ChatMemberUpdated,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
)

from config import ADMIN_ID
from database.queries import save_group, remove_group, get_all_groups

router = Router(name="broadcast")


class BroadcastState(StatesGroup):
    waiting_message = State()


def is_admin(message: Message) -> bool:
    return message.from_user.id == ADMIN_ID


# ─── Отслеживание добавления / удаления бота из групп ────────────────────────

@router.my_chat_member()
async def on_chat_member_update(event: ChatMemberUpdated) -> None:
    chat = event.chat
    if chat.type not in ("group", "supergroup"):
        return

    new_status = event.new_chat_member.status

    if new_status in ("member", "administrator"):
        await save_group(chat.id, chat.title or "")
    elif new_status in ("left", "kicked", "banned"):
        await remove_group(chat.id)


# ─── Рассылка: /broadcast ─────────────────────────────────────────────────────

@router.message(Command("broadcast"))
async def broadcast_start(message: Message, state: FSMContext) -> None:
    if not is_admin(message):
        return

    groups = await get_all_groups()

    if not groups:
        await message.answer(
            "⚠️ Бот ещё не добавлен ни в одну группу.\n"
            "Добавь бота в группу — он запомнит её автоматически."
        )
        return

    group_list = "\n".join(f"• {g['title'] or g['chat_id']}" for g in groups)

    cancel_kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отменить")]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await state.set_state(BroadcastState.waiting_message)
    await message.answer(
        f"📢 <b>Рассылка в группы</b>\n\n"
        f"Групп найдено: <b>{len(groups)}</b>\n"
        f"{group_list}\n\n"
        f"Напиши сообщение которое хочешь отправить во все группы:",
        reply_markup=cancel_kb,
        parse_mode="HTML",
    )


@router.message(BroadcastState.waiting_message)
async def broadcast_send(message: Message, state: FSMContext, bot: Bot) -> None:
    if message.text == "❌ Отменить":
        await state.clear()
        await message.answer("❌ Рассылка отменена.", reply_markup=ReplyKeyboardRemove())
        return

    groups = await get_all_groups()
    await state.clear()

    sent = 0
    failed = 0

    for group in groups:
        try:
            await bot.send_message(
                chat_id=group["chat_id"],
                text=message.text,
                parse_mode="HTML",
            )
            sent += 1
        except Exception:
            await remove_group(group["chat_id"])
            failed += 1

    await message.answer(
        f"✅ <b>Рассылка завершена!</b>\n\n"
        f"📨 Отправлено: <b>{sent}</b>\n"
        f"❌ Ошибок (группа удалена из списка): <b>{failed}</b>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode="HTML",
    )
