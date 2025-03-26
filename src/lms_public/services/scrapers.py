import aiohttp
from bs4 import BeautifulSoup

from common.models import LMSCookie
from common.services import constants
from lms_public.models import LMSCourse, PublicMessage
from lms_public.services.parsers import parse_public_message


async def get_page_text(suffix_url: str, cookie: LMSCookie) -> str:
    """Get the page text from LMS. Sends request to URL and return the text.
    Encoding is set to response.charset (UTF-8). However, some messages have
    have character which cannot be decoded. So, `errors="replace"` is used.

    Args:
        suffix_url (str): URL to send request to
        cookie (LMSCookie): An LMSCookie instance

    Returns:
        (str): Page text
    """
    BASE_URL = constants.BASE_URL

    async with aiohttp.ClientSession(
        base_url=BASE_URL, cookies=cookie.as_dict
    ) as session:
        async with session.get(url=suffix_url) as response:
            if response.status == 200:
                return await response.text(
                    encoding=response.charset, errors="replace"
                )
            return ""


async def get_courses_suffix_urls(
    cookie: LMSCookie,
) -> list[tuple[str, str]]:
    """Get the course codes from LMS. Sends request to home page.
    Parses the text using bs4.
    Args:
        cookie (str): An LMSCookie instance

    Returns:
        list[tuple[str, str]]: List of (course_suffix_url, course_name) tuples
    """
    HOME_SUFFIX_URL = constants.HOME_SUFFIX_URL
    page_text = await get_page_text(suffix_url=HOME_SUFFIX_URL, cookie=cookie)
    soup = BeautifulSoup(page_text, "html.parser")
    li_tags = soup.find(id="profile_groups").find_all("li")
    courses_info = list()
    for li_tag in li_tags:
        course_suffix_url = li_tag.find("a").get("href")
        course_name = li_tag.find_all("div")[1].text.split("\t")[1].strip()
        single_info = (course_suffix_url, course_name)
        courses_info.append(single_info)
    return courses_info


async def get_course_messages(
    course: LMSCourse, cookie: LMSCookie
) -> list[PublicMessage]:
    """Get the course messages from LMS. Sends request to course page.
    Parses the text using bs4.

    Args:
        course (LMSCourse): An LMSCourser instance
        cookie (LMSCookie): An LMSCookie instance

    Returns:
        (list[PublicMessage]): List of course messages
    """
    page_text = await get_page_text(
        suffix_url=course.suffix_url, cookie=cookie
    )

    # Begin scrape
    soup = BeautifulSoup(page_text, "html.parser")
    message_containers = soup.find_all(class_="wall-action-item")
    parsed_messages = list()
    for msg_container in message_containers:
        parsed_messages.append(
            parse_public_message(
                message_container=msg_container,
                course=course,
            )
        )
    return parsed_messages
