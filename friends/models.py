from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models


class UserFriend(models.Model):
    """Representation of user friends"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='user')
    friend = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friend')
    created = models.DateTimeField(auto_now_add=True)
    share_all_lists = models.BooleanField(default=0)

    class Meta:
        unique_together = ('user', 'friend')


class Invite(models.Model):
    """Representation of invites to friends list"""
    send_from = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='send_from')
    send_to = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='send_to', null=True)
    requested_friend_username = models.CharField(max_length=255)
    send_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('send_from', 'requested_friend_username')
