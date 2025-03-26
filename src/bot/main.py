import asyncio
import logging
import os
import sys

import django
from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove, BotCommand
from asgiref.sync import sync_to_async
from celery import chain
from django.db import transaction
from dotenv import load_dotenv


def setup_django():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core_config.settings")
    django.setup()


# Call this function before importing Django models
setup_django()

from bot.tasks import send_welcome_message_task  # noqa
from common.models import ChatID, LMSUser  # noqa
from common.services.cookie import get_cookie  # noqa
from lms_public.schedule_tasks import schedule_periodic_tasks  # noqa
from lms_public.tasks import check_new_messages_task, update_user_courses_task  # noqa

load_dotenv(override=True)

TOKEN = os.environ.get("BOT_TOKEN")
form_router = Router()


class Form(StatesGroup):
    lms_username = State()
    lms_password = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    """Triggered by /start command in Telegram

    Args:
        message (Message): The message sent by user
        state (FSMContext): The state in which user is
    """

    await message.answer(
        "سلام!\n"
        "به یونیف خوش اومدین. برای ورود به حسابتون دستور"
        " /login "
        "رو بزنید.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("cancel"))
@form_router.message(F.text.casefold() == "cancel")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """Allow the user to cancel any action

    Args:
        message (Message): The cancel command (/cancel)
        state (FSMContext): The state in which the user is
    """

    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "عملیات لغو شد.",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("login"))
async def process_login_command(message: Message, state: FSMContext) -> None:
    """Receive LMS Username

    Args:
        message (Message): The login command (/login)
        state (FSMContext): The state in which the user is
    """

    await state.set_state(Form.lms_username)
    await message.answer("لطفا نام کاربری LMS خود را وارد کنید:")


@form_router.message(Form.lms_username)
async def process_lms_username(message: Message, state: FSMContext) -> None:
    """Save LMS Username

    Args:
        message (Message): The message containing LMS Username
        state (FSMContext): The state in which the user is
    """

    username = message.text
    await state.update_data(lms_username=username)
    await state.set_state(Form.lms_password)
    await message.answer("لطفا رمز عبور LMS خود را وارد کنید:")


@transaction.atomic
@form_router.message(Form.lms_password)
async def process_lms_password(message: Message, state: FSMContext) -> None:
    """Save LMS Password and start the process

    Args:
        message (Message): The message containing LMS Password
        state (FSMContext): The state in which the user is
    """

    password = message.text
    data = await state.get_data()
    username = data.get("lms_username")
    lms_user, created = await LMSUser.objects.aget_or_create(
        username=username, password=password
    )
    if not created:
        await message.answer(
            f"کاربر {username} قبلا در سیستم ثبت نام شده است.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.clear()
        return

    # get_login
    cookie = await get_cookie(user=lms_user)
    if not cookie.cookie:
        await message.answer(
            f"ورود با نام کاربری {username} ناموفق بود.",
            reply_markup=ReplyKeyboardRemove(),
        )
        await lms_user.adelete()
        await state.clear()
        return

    await ChatID.objects.aupdate_or_create(
        user=lms_user,
        defaults={
            "chat_id": message.chat.id,
        },
    )
    await sync_to_async(
        lambda: transaction.on_commit(
            chain(
                update_user_courses_task.si(user_id=lms_user.pk),
                check_new_messages_task.si(
                    user_id=lms_user.pk, is_first_time=True
                ),
                send_welcome_message_task.s(chat_id=message.chat.id),
            ).delay
        )
    )()

    await schedule_periodic_tasks(user_id=lms_user.pk)

    await state.clear()

@form_router.message(Command("chat_id"))
async def get_chat_id(message: Message) -> None:
    """Get the current chat ID
    
    Args:
        message (Message): The message sent by user
    """
    chat_id = message.chat.id
    await message.answer(
        f"آیدی چت شما:\n<code>{chat_id}</code>",
        parse_mode=ParseMode.HTML
    )


async def set_commands(bot: Bot):
    """Set bot commands to show in the menu"""
    commands = [
        BotCommand(command="start", description="شروع کار با ربات"),
        BotCommand(command="chat_id", description="دریافت آیدی چت فعلی"),
        BotCommand(command="login", description="ورود به سامانه LMS"),
        BotCommand(command="cancel", description="لغو عملیات فعلی")
        # Add other commands as needed
    ]
    await bot.set_my_commands(commands)


async def main():
    """Run the bot with the form_router included"""

    bot = Bot(
        token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    dp.include_router(form_router)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
