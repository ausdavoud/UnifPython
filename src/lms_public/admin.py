from django.contrib import admin

from lms_public.models import LMSCourse, PublicMessage

# Register your models here.
admin.site.register(PublicMessage)
admin.site.register(LMSCourse)
