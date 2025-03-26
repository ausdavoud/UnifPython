from django.db import models

from common.models import LMSUser, TimeStampBaseModel


class LMSCourse(TimeStampBaseModel):
    user = models.ForeignKey(
        LMSUser, related_name="courses", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128)
    suffix_url = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}"


class PublicMessage(TimeStampBaseModel):
    user = models.ForeignKey(
        LMSUser, related_name="public_messages", on_delete=models.CASCADE
    )
    item_id = models.CharField(max_length=64)
    lms_course = models.ForeignKey(
        LMSCourse, related_name="messages", on_delete=models.CASCADE
    )
    author = models.CharField(max_length=64)
    text = models.TextField(blank=True)  # For online sessions
    header = models.TextField(blank=True)
    footer = models.TextField(blank=True)
    sent_at = models.CharField(max_length=64)
    has_attachment = models.BooleanField(default=False)
    attachment_name = models.CharField(max_length=128, blank=True)
    attachment_link = models.CharField(max_length=256, blank=True)
    is_exercise = models.BooleanField(default=False)
    is_exercise_finished = models.BooleanField(default=False)
    exercise_name = models.CharField(max_length=128, blank=True)
    exercise_start = models.CharField(max_length=64, blank=True)
    exercise_deadline = models.CharField(max_length=64, blank=True)
    is_online_session = models.BooleanField(default=False)
    online_session_name = models.CharField(max_length=128, blank=True)
    online_session_link = models.CharField(max_length=256, blank=True)
    online_session_status = models.CharField(max_length=64, blank=True)
    online_session_start = models.CharField(max_length=64, blank=True)
    online_session_end = models.CharField(max_length=64, blank=True)

    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} <-> {self.author}"


class UserNotificationPreference(models.Model):
    user = models.OneToOneField(LMSUser, on_delete=models.CASCADE)
    public_lms_interval_minutes = models.PositiveIntegerField(default=5)
