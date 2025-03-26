import aiohttp

from common.models import LMSCookie, LMSUser
from common.services import constants


async def login(user: LMSUser) -> LMSCookie:
    """Login to LMS. `BASE_URL` and `LOGIN_SUFFIX_URL` are taken from
    constants.py. If status is 302, request is being redirected
    to the home page, so the login is successful. If not, session
    is still at the login page, so it was not successful.

    Args:
        user (LMSUser): LMSUser instance

    Returns:
        (LMSCookie): An LMSCookie
    """

    BASE_URL = constants.BASE_URL
    LOGIN_SUFFIX_URL = constants.LOGIN_SUFFIX_URL
    json_body = {"username": user.username, "password": user.decoded_password}

    async with aiohttp.ClientSession(base_url=BASE_URL) as session:
        async with session.post(
            url=LOGIN_SUFFIX_URL, data=json_body, allow_redirects=False
        ) as response:
            if response.status == 302 and response.cookies.get(
                constants.COOKIE_KEY_NAME, False
            ):
                return LMSCookie(
                    cookie=response.cookies[constants.COOKIE_KEY_NAME].value
                )
            return LMSCookie(cookie="")


async def is_cookie_valid(cookie: LMSCookie) -> bool:
    """Send request to /members/home to see if cookie has expired.
    If response is 302, request is being redirected to the login page.
    So, the cookie was expired (or invalid). If not, it's reached /members/home.

    Args:
        cookie (LMSCookie): An LMSCookie

    Returns:
        (bool): True if we're not redirected to another page (login),
        False if redirected.
    """

    BASE_URL = constants.BASE_URL
    HOME_SUFFIX_URL = constants.HOME_SUFFIX_URL

    async with aiohttp.ClientSession(
        base_url=BASE_URL, cookies=cookie.as_dict
    ) as session:
        async with session.get(
            url=HOME_SUFFIX_URL, allow_redirects=False
        ) as response:
            if response.status == 302:
                return False
            return True


async def get_cookie(user: LMSUser) -> LMSCookie:
    """Find cookie in database. if not found or invalid,
    logins to get a new cookie str and stores it in the database.

    Args:
        user (LMSUser): LMS User instance

    Returns:
        (LMSCookie): An LMSCookie
    """

    cookie_value = await LMSCookie.objects.filter(user=user).afirst()
    cookie_value = cookie_value.cookie if cookie_value else ""
    cookie = LMSCookie(user=user, cookie=cookie_value)
    is_valid = await is_cookie_valid(cookie=cookie)
    if is_valid:
        return cookie
    cookie = await login(user=user)
    await LMSCookie.objects.aupdate_or_create(
        user=user,
        defaults={"cookie": cookie.cookie},
    )
    return cookie
