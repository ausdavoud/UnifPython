from django.contrib import admin

from common.models import ChatID, LMSCookie, LMSUser

admin.site.register(LMSUser)
admin.site.register(LMSCookie)
admin.site.register(ChatID)
