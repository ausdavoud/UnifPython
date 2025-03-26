from asgiref.sync import sync_to_async

from common.services import constants
from lms_public.models import PublicMessage


def on_is_exercise(
    new_message: PublicMessage, old_message: PublicMessage
) -> None:
    """Handle exercise status change"""
    message = new_message if new_message.is_exercise else old_message
    exercise_name = message.exercise_name if message.exercise_name else ""
    action = "اضافه شد." if new_message.is_exercise else "حذف شد."
    new_message.header = f"تمرین {exercise_name} {action}"


def on_is_exercise_finished(
    new_message: PublicMessage, old_message: PublicMessage
) -> None:
    """Handle exercise completion status change"""
    exercise_name = (
        new_message.exercise_name if new_message.exercise_name else ""
    )
    action = (
        "به پایان رسید." if new_message.is_exercise_finished else "تغییر کرد."
    )
    new_message.header = f"مهلت ارسال تمرین {exercise_name} {action}"


def on_has_attachment(
    new_message: PublicMessage,
    old_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle attachment status change"""
    minor_action = "افزودن" if new_message.has_attachment else "حذف"
    major_action = "اضافه شد." if new_message.has_attachment else "حذف شد."
    message = new_message if new_message.has_attachment else old_message
    attachment_name = (
        message.attachment_name if message.attachment_name else ""
    )

    if has_major_change:
        minor_changes.append(f"{minor_action} فایل پیوست")
    else:
        new_message.header = f"فایل پیوست {attachment_name} {major_action}"


def on_exercise_deadline(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle exercise deadline change"""
    exercise_name = (
        new_message.exercise_name if new_message.exercise_name else ""
    )
    alert_if_still_finished = (
        "اما مهلت همچنان تمام شده است."
        if new_message.is_exercise_finished
        else ""
    )
    if has_major_change:
        minor_changes.append("تغییر مهلت ارسال تمدید")
    else:
        new_message.header = (
            f"مهلت ارسال تمرین {exercise_name} تغییر کرد. "
            f"{alert_if_still_finished}"
        )


def on_attachment_link_and_text(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle attachment link and text change"""
    attachment_name = (
        f"به نام {new_message.attachment_name}"
        if new_message.attachment_name
        else ""
    )
    if has_major_change:
        minor_changes.append("آپلود فایل پیوست جدید")
    else:
        new_message.header = f"فایل پیوست جدیدی {attachment_name} آپلود شد."


def on_attachment_link(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle attachment link change"""
    if has_major_change:
        minor_changes.append("تغییر لینک فایل پیوست")
    else:
        new_message.header = "لینک فایل پیوست تغییر کرد."


def on_attachment_name(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle attachment name change"""
    if has_major_change:
        minor_changes.append("تغییر نام فایل پیوست")
    else:
        new_message.header = "نام فایل پیوست تغییر کرد."


def on_exercise_name(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle exercise name change"""
    name_and_action = (
        f"به {new_message.exercise_name} تغییر کرد."
        if new_message.exercise_name
        else "حذف شد."
    )
    if has_major_change:
        minor_changes.append("تغییر نام تمرین")
    else:
        new_message.header = f"نام تمرین {name_and_action}"


def on_exercise_start(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle exercise start time change"""
    if has_major_change:
        minor_changes.append("تغییر زمان شروع تمرین")
    else:
        new_message.header = (
            f"زمان شروع تمرین را به {new_message.exercise_start} تغییر کرد."
        )


def on_is_online_session(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle online session status change"""
    if has_major_change:
        minor_changes.append("ایجاد یک جلسه‌ی آنلاین")
    else:
        new_message.header = "یک جلسه‌ی آنلاین جدید ایجاد شد."


def on_online_session_name(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle online session name change"""
    if has_major_change:
        minor_changes.append("تغییر نام جلسه آنلاین")
    else:
        new_message.header = (
            f"نام جلسه آنلاین به {new_message.online_session_name} تغییر کرد."
        )


def on_online_session_link(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle online session link change"""
    if has_major_change:
        minor_changes.append("تغییر لینک جلسه آنلاین")
    else:
        new_message.header = "لینک جلسه آنلاین تغییر کرد."


def on_online_session_status(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle online session status change"""
    if has_major_change:
        minor_changes.append("تغییر وضعیت جلسه آنلاین")
    else:
        new_message.header = f"وضعیت جلسه آنلاین به {new_message.online_session_status} تغییر کرد."


def on_online_session_start(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle online session start time change"""
    if has_major_change:
        minor_changes.append("تغییر زمان شروع جلسه آنلاین")
    else:
        new_message.header = f"زمان شروع جلسه آنلاین به {new_message.online_session_start} تغییر کرد."


def on_online_session_end(
    new_message: PublicMessage,
    has_major_change: bool,
    minor_changes: list[str],
) -> None:
    """Handle online session end time change"""
    if has_major_change:
        minor_changes.append("تغییر زمان پایان جلسه آنلاین")
    else:
        new_message.header = f"زمان پایان جلسه آنلاین به {new_message.online_session_end} تغییر کرد."


def is_x_changed(
    old_message: PublicMessage, new_message: PublicMessage
) -> dict[str, bool]:
    """Check which properties have changed between messages"""
    return {
        "is_exercise_changed": old_message.is_exercise
        != new_message.is_exercise,
        "is_exercise_finished_changed": old_message.is_exercise_finished
        != new_message.is_exercise_finished,
        "is_exercise_deadline_changed": old_message.exercise_deadline
        != new_message.exercise_deadline,
        "is_has_attachment_changed": old_message.has_attachment
        != new_message.has_attachment,
        "is_attachment_link_changed": old_message.attachment_link
        != new_message.attachment_link,
        "is_attachment_name_changed": old_message.attachment_name
        != new_message.attachment_name,
        "is_exercise_name_changed": old_message.exercise_name
        != new_message.exercise_name,
        "is_exercise_start_changed": old_message.exercise_start
        != new_message.exercise_start,
        "is_online_session_changed": old_message.is_online_session
        != new_message.is_online_session,
        "is_online_session_name_changed": old_message.online_session_name
        != new_message.online_session_name,
        "is_online_session_link_changed": old_message.online_session_link
        != new_message.online_session_link,
        "is_online_session_status_changed": old_message.online_session_status
        != new_message.online_session_status,
        "is_online_session_start_changed": old_message.online_session_start
        != new_message.online_session_start,
        "is_online_session_end_changed": old_message.online_session_end
        != new_message.online_session_end,
    }


def add_message_header_footer(
    new_message: PublicMessage, old_message: PublicMessage | None
) -> None:
    """Add appropriate header and footer to message based on changes"""
    has_major_change = False
    if not old_message:
        # The major change is being a new message
        has_major_change = True
        return has_major_change

    changes = is_x_changed(old_message, new_message)
    minor_changes: list[str] = list()

    if changes["is_exercise_changed"]:
        on_is_exercise(new_message, old_message)
        has_major_change = True
        return has_major_change

    if changes["is_exercise_finished_changed"]:
        on_is_exercise_finished(new_message, old_message)
        has_major_change = True

    if (
        changes["is_exercise_deadline_changed"]
        and not changes["is_exercise_finished_changed"]
    ):
        on_exercise_deadline(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_has_attachment_changed"]:
        on_has_attachment(
            new_message, old_message, has_major_change, minor_changes
        )
        has_major_change = True
    elif (
        changes["is_attachment_link_changed"]
        and changes["is_attachment_name_changed"]
    ):
        on_attachment_link_and_text(
            new_message, has_major_change, minor_changes
        )
        has_major_change = True
    elif changes["is_attachment_link_changed"]:
        on_attachment_link(new_message, has_major_change, minor_changes)
        has_major_change = True
    elif changes["is_attachment_name_changed"]:
        on_attachment_name(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_exercise_name_changed"]:
        on_exercise_name(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_exercise_start_changed"]:
        on_exercise_start(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_online_session_changed"]:
        on_is_online_session(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_online_session_name_changed"]:
        on_online_session_name(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_online_session_link_changed"]:
        on_online_session_link(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_online_session_status_changed"]:
        on_online_session_status(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_online_session_start_changed"]:
        on_online_session_start(new_message, has_major_change, minor_changes)
        has_major_change = True

    if changes["is_online_session_end_changed"]:
        on_online_session_end(new_message, has_major_change, minor_changes)
        has_major_change = True

    if minor_changes:
        footer_items = (
            "\n- ".join(minor_changes)
            if isinstance(minor_changes, list)
            else minor_changes
        )
        new_message.footer = footer_items

    return has_major_change


def has_message_changed(
    new_message: PublicMessage, old_message: PublicMessage | None
) -> bool:
    """Determine if message has changed"""
    if not old_message:
        return True

    changes = is_x_changed(old_message, new_message)
    return any(changes.values())


async def public_message_to_html(message: PublicMessage) -> str:
    """
    Converts a PublicMessage object to HTML representation.

    Args:
        message: PublicMessage object to convert

    Returns:
        str: HTML representation of the message
    """
    course_name = await sync_to_async(lambda: message.lms_course.name)()
    course_name = f"📚  {course_name}"

    author = f"\n\n👤  {message.author}"
    header = f"\n\n▫️<b>{message.header}</b>" if message.header else ""

    # Assuming 'text' field exists in PublicMessage but wasn't shown in the provided code
    text = (
        f"\n\n✍🏻  {message.text}"
        if hasattr(message, "text") and message.text
        else ""
    )

    footer = ""
    if hasattr(message, "footer") and message.footer:
        footer = f"\n\nتغییرات جزئی: \n{message.footer}"

    exercise_description = ""
    if message.is_exercise:
        exercise_description = (
            f"\n\nنام تمرین: {message.exercise_name}\n"
            f"زمان شروع: {message.exercise_start}\n"
            f"مهلت ارسال: {message.exercise_deadline}"
        )
        if message.is_exercise_finished:
            exercise_description += "(پایان یافته) "

    attachment_description = ""
    if message.has_attachment:
        attachment_description = f'\n\nفایل: <a href="{constants.BASE_URL + message.attachment_link}">{message.attachment_name}</a>'

    online_session_description = ""
    if message.is_online_session:
        online_session_status_icon = "⏳"
        if "در حال" in message.online_session_status:
            online_session_status_icon = "🟢"
        elif "ضبط" in message.online_session_status:
            online_session_status_icon = "🔴"
        online_session_description = (
            f'\n\n🌐 عنوان جلسه: <a href="{constants.BASE_URL + message.online_session_link}">{message.online_session_name}</a>'
            f"\n{online_session_status_icon} وضعیت: {message.online_session_status}"
            f"\n🚀 زمان شروع: {message.online_session_start}"
            f"\n🏁 زمان پایان: {message.online_session_end}"
        )
    # Assuming 'sentAt' field exists in PublicMessage but wasn't shown in the provided code
    date = (
        f"\n\n🕑  {message.sent_at}"
        if hasattr(message, "sent_at") and message.sent_at
        else ""
    )

    white_space = "‌"  # Zero-width non-joiner character

    message_html = (
        f"{course_name}"
        f"{author}"
        f"{header}"
        f"{text}"
        f"{footer}"
        f"{exercise_description}"
        f"{attachment_description}"
        f"{online_session_description}"
        f"{date}"
        f"{white_space}\n"
    )

    return message_html
