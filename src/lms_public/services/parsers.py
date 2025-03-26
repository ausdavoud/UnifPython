from bs4 import BeautifulSoup

from lms_public.models import PublicMessage


def parse_public_message(
    message_container: BeautifulSoup, course: str
) -> PublicMessage:
    """Parse a message li element and extract all relevant information.

    Args:
        message_container (BeautifulSoup): BeautifulSoup element representing the message
        course (LMSCourse): An LMSCourse instance

    Returns:
        (dict): Dictionary containing message details
    """
    # Initialize message data
    message = {
        "item_id": "",
        "lms_course": course,
        "author": "",
        "text": "",
        "sent_at": "",
        "has_attachment": False,
        "attachment_name": "",
        "attachment_link": "",
        "is_exercise": False,
        "is_exercise_finished": False,
        "exercise_name": "",
        "exercise_start": "",
        "exercise_deadline": "",
        "is_online_session": False,
        "online_session_name": "",
        "online_session_link": "",
        "online_session_status": "",
        "online_session_start": "",
        "online_session_end": "",
    }

    # Extract item id
    # find the id of the message container
    message["item_id"] = message_container.get("id")

    # Extract author
    author_element = message_container.select_one(
        'a[class~="feed_item_username"]'
    )
    if author_element:
        # this converts "Fakheran - Ali" to "Ali Fakheran"
        message["author"] = " ".join(
            reversed(author_element.text.strip().split(" - "))
        )

    # Extract text body
    text_body = message_container.select_one(
        'span[class="feed_item_bodytext"]'
    )
    if text_body:
        # Check for expanded text content
        text_span = text_body.select_one(
            'span[class="view_more"][style^="display"]'
        )
        text_element = (
            text_span if text_span and text_span.text.strip() else text_body
        )
        message["text"] = text_element.text.strip()

    # Extract timestamp
    timestamp_element = message_container.select_one('span[class="timestamp"]')
    if timestamp_element:
        message["sent_at"] = timestamp_element.text.strip()

    # Check for attachments
    attachment_div = message_container.select_one(
        'div[class="feed_item_attachments"]'
    )
    if attachment_div:
        online_session_table = attachment_div.find("table")
        if online_session_table:
            message["is_online_session"] = True
            message["online_session_name"] = online_session_table.find(
                class_="adobe_meeting_url"
            ).text
            message["online_session_link"] = online_session_table.find(
                class_="adobe_meeting_url"
            ).get("href", "")
            message["online_session_status"] = (
                online_session_table.find_all("tr")[-1]
                .find_all("td")[2]
                .find("span")
                .text
            )
            online_session_time = (
                online_session_table.find_all("tr")[-1]
                .find_all("td")[2]
                .find("div")
                .text
            )
            start_part, end_part = online_session_time.split("زمان پایان : ")
            start_time = start_part.replace("زمان شروع : ", "").strip()
            end_time = end_part.strip()
            message["online_session_start"] = start_time
            message["online_session_end"] = end_time

        else:
            attachment_spans = attachment_div.find_all("span", recursive=False)
            if len(attachment_spans) == 0:
                # Regular attachment, not an exercise
                message["has_attachment"] = True
                anchor_tag = attachment_div.find("a")
                if anchor_tag:
                    message["attachment_name"] = anchor_tag.text.strip()
                    message["attachment_link"] = anchor_tag.get("href", "")

            if len(attachment_spans) == 1:
                # It's a link
                link = (
                    attachment_spans[0]
                    .find(class_="feed_item_link_title")
                    .text.strip()
                )
                if link not in message["text"]:
                    message["text"] += f"\n{link}"

            elif len(attachment_spans) == 4:
                # It's an exercise
                message["is_exercise"] = True

                # Extract exercise name
                exercise_name = attachment_spans[0].text.strip()
                # Remove "title:" prefix
                colon_index = exercise_name.find(":")
                if colon_index != -1:
                    message["exercise_name"] = exercise_name[
                        colon_index + 1 :
                    ].strip()

                # Check for exercise attachment
                if attachment_spans[1].find("a"):
                    anchor_tag = attachment_spans[1].find("a")
                    message["has_attachment"] = True
                    message["attachment_name"] = anchor_tag.text.strip()
                    message["attachment_link"] = anchor_tag.get("href", "")

                # Extract exercise start time

                exercise_start = attachment_spans[2].text.strip()
                colon_index = exercise_start.find(":")
                if colon_index != -1:
                    message["exercise_start"] = exercise_start[
                        colon_index + 1 :
                    ].strip()

                # Extract exercise deadline
                exercise_deadline = attachment_spans[3].text.strip()
                colon_index = exercise_deadline.find(":")
                if colon_index != -1:
                    message["exercise_deadline"] = exercise_deadline[
                        colon_index + 1 :
                    ].strip()
                    if "پایان" in message["exercise_deadline"]:
                        message["is_exercise_finished"] = True

    return PublicMessage(**message)
