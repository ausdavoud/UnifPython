import os

import aiohttp
from aiogram.enums import ParseMode

from lms_public.models import PublicMessage
from lms_public.services.change_handler import public_message_to_html


async def send_notifications_service(chat_id: int, lms_msg_id: int) -> None:
    """Send a previously saved message to a certain chat id

    Args:
        chat_id (int): A Telegram chat id
        lms_msg_id (int): The id of the message in database
    """

    lms_msg = await PublicMessage.objects.aget(id=lms_msg_id)
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    html_message = await public_message_to_html(message=lms_msg)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": html_message,
                "parse_mode": ParseMode.HTML,
            },
        ) as response:
            if response.status == 200:
                lms_msg.is_sent = True
                await lms_msg.asave()
            else:
                # Delete it, to be fetched again
                await lms_msg.adelete()


async def send_welcome_message_service(msg_count: int, chat_id: int) -> None:
    """Send a welcome message to a certain chat id

    Args:
        msg_count (int): The number of scraped messages
        chat_id (int): A Telegram chat id
    """

    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    async with aiohttp.ClientSession() as session:
        await session.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": f"تعداد {msg_count} پیام پردازش و اعلان‌های جدید اطلاع‌رسانی خواهند شد",
                "parse_mode": ParseMode.HTML,
            },
        )
