import asyncio

from celery import shared_task

from lms_public.services.scheduled_tasks import check_new_messages_service
from lms_public.services.scheduled_tasks import update_user_courses_service


@shared_task(ignore_result=True)
def update_user_courses_task(user_id: int) -> None:
    asyncio.run(update_user_courses_service(user_id=user_id))


@shared_task
def check_new_messages_task(user_id: int, is_first_time: bool = False) -> int:
    return asyncio.run(
        check_new_messages_service(
            user_id=user_id, is_first_time=is_first_time
        )
    )
