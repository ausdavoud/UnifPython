import json

from django_celery_beat.models import (
    CrontabSchedule,
    IntervalSchedule,
    PeriodicTask,
)

from lms_public.models import UserNotificationPreference


# Schedule to run every Thursday at midnight (UTC)
async def schedule_periodic_tasks(user_id: int):
    """Schedule 2 periodic tasks:
    1. Update courses every Thursday at midnight
    2. Check messages every 5 minutes

    Args:
        user_id (int): The id of the LMSUser instance
    """

    # Task 1: Every Thursday at midnight
    thursday_schedule, _ = await CrontabSchedule.objects.aget_or_create(
        minute="0",
        hour="0",
        day_of_week="4",  # Thursday
        day_of_month="*",
        month_of_year="*",
    )
    await PeriodicTask.objects.aupdate_or_create(
        name=f"Update courses for user {user_id}",
        task="lms_public.tasks.update_user_courses_task",
        defaults={
            "crontab": thursday_schedule,
            "args": json.dumps([user_id]),
        },
    )

    # Task 2: Every 5 minutes (or user-defined interval)
    user_pref, _ = await UserNotificationPreference.objects.aget_or_create(
        user_id=user_id,
        defaults={"public_lms_interval_minutes": 5},
    )
    interval_schedule, _ = await IntervalSchedule.objects.aget_or_create(
        every=user_pref.public_lms_interval_minutes,
        period=IntervalSchedule.MINUTES,
    )
    await PeriodicTask.objects.aupdate_or_create(
        name=f"Check messages for user {user_id}",
        task="lms_public.tasks.check_new_messages_task",
        defaults={
            "interval": interval_schedule,
            "args": json.dumps([user_id]),
        },
    )
