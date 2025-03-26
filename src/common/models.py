from django.db import models

from common.services import constants


class TimeStampBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class LMSUser(TimeStampBaseModel):
    username = models.CharField(max_length=10)
    password = models.CharField(max_length=128)

    @property
    def decoded_password(self):
        return self.password

    def __str__(self):
        return self.username


class LMSCookie(TimeStampBaseModel):
    user = models.OneToOneField(
        LMSUser, on_delete=models.CASCADE, related_name="cookie"
    )
    cookie = models.CharField(max_length=256)

    @property
    def as_dict(self):
        return {constants.COOKIE_KEY_NAME: self.cookie}

    def __str__(self):
        return self.cookie


class ChatID(TimeStampBaseModel):
    user = models.OneToOneField(
        LMSUser, on_delete=models.CASCADE, related_name="chat_id"
    )
    chat_id = models.CharField(max_length=64)

    def __str__(self):
        return self.chat_id
