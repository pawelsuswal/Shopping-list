from django.contrib import admin

from friends import models

# Register your models here.
admin.site.register(models.Invite)
admin.site.register(models.UserFriend)