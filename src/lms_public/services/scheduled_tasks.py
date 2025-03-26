import asyncio

from asgiref.sync import sync_to_async

from bot.tasks import send_notifications_task
from common.models import LMSUser
from common.services.cookie import get_cookie
from lms_public.models import LMSCourse, PublicMessage
from lms_public.services.change_handler import add_message_header_footer
from lms_public.services.scrapers import (
    get_course_messages,
    get_courses_suffix_urls,
)


async def update_user_courses_service(user_id: int) -> None:
    """Fetch new LMS courses and mark them as active,
    deactivating older ones

    Args:
        user_id (int): The id of the LMS User
    """

    lms_user = await LMSUser.objects.aget(id=user_id)
    cookie = await get_cookie(user=lms_user)
    courses_info = await get_courses_suffix_urls(cookie=cookie)
    all_suffix_urls = [info[0] for info in courses_info]

    for crs_info in courses_info:
        await LMSCourse.objects.aget_or_create(
            user=lms_user,
            suffix_url=crs_info[0],
            defaults={"name": crs_info[1]},
        )
    # Deactivate old courses
    await (
        LMSCourse.objects.exclude(
            suffix_url__in=all_suffix_urls,
        )
        .filter(user=lms_user)
        .aupdate(is_active=False)
    )


async def check_new_messages_service(
    user_id: int, is_first_time: bool = False
) -> int:
    """Fetch new messages, compare them with the old ones, send notification
    for the new ones

    Args:
        user_id (int): The id of the LMSUser instance
        is_first_time (bool, optional): If true, sends notification for every
            new message. If false, does not send any message. The return value
            then can be used to send a welcome message, containing the number of
            scraped messages. Defaults to False.

    Returns:
        int: The number of scraped messages
    """

    lms_user = await LMSUser.objects.aget(id=user_id)
    cookie = await get_cookie(user=lms_user)
    chat_id = await sync_to_async(lambda: lms_user.chat_id.chat_id)()
    active_courses = await sync_to_async(list)(
        LMSCourse.objects.filter(user=lms_user, is_active=True)
    )
    tasks = [
        asyncio.create_task(get_course_messages(course=course, cookie=cookie))
        for course in active_courses
    ]
    courses_messages = await asyncio.gather(*tasks)

    msg_count = 0
    for crs_messages in courses_messages:
        for lms_msg in crs_messages:
            db_msg = await PublicMessage.objects.filter(
                user=lms_user,
                item_id=lms_msg.item_id,
                lms_course__suffix_url=lms_msg.lms_course.suffix_url,
                author=lms_msg.author,
                sent_at=lms_msg.sent_at,
            ).alast()

            if add_message_header_footer(
                new_message=lms_msg, old_message=db_msg
            ):
                lms_msg.user = lms_user
                await lms_msg.asave()
                msg_count += 1
                if is_first_time:
                    continue
                send_notifications_task.delay(
                    chat_id=chat_id, lms_msg_id=lms_msg.pk
                )
    return msg_count
