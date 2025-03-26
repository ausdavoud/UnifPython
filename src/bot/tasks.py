import asyncio

from celery import shared_task

from bot.services import send_notifications_service
from bot.services import send_welcome_message_service


@shared_task(ignore_result=True)
def send_notifications_task(chat_id: int, lms_msg_id: int) -> None:
    asyncio.run(
        send_notifications_service(chat_id=chat_id, lms_msg_id=lms_msg_id)
    )


@shared_task(ignore_result=True)
def send_welcome_message_task(msg_count: int, chat_id: int) -> None:
    asyncio.run(
        send_welcome_message_service(msg_count=msg_count, chat_id=chat_id)
    )
