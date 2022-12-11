from django import forms
from django.core.exceptions import ValidationError

from friends.models import Invite, UserFriend


class InviteCreateForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ('requested_friend_username',)
        labels = {
            'requested_friend_username': 'Enter friend username'
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request')
        super(InviteCreateForm, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        requested_username = self.cleaned_data.get('requested_friend_username')
        user = self.request.user
        if requested_username == user.username:
            raise ValidationError('You cannot invite yourself')
        friends = UserFriend.objects.filter(user=user, friend__username=requested_username)
        if friends:
            raise ValidationError('You are already friends')
        invite = Invite.objects.filter(send_from=user, requested_friend_username=requested_username)
        if invite:
            raise ValidationError('You already invited that person')

        return super().clean()


class InviteListForm(forms.ModelForm):
    class Meta:
        model = Invite
        fields = ('requested_friend_username',)
        labels = {
            'requested_friend_username': 'Username'
        }
