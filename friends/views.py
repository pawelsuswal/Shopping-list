from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django import views

from friends.forms import InviteCreateForm
from friends.models import UserFriend, Invite


class InviteCreateView(LoginRequiredMixin, CreateView):
    model = Invite
    form_class = InviteCreateForm
    success_url = reverse_lazy('friends:friends_list')
    template_name = 'friends/create_invite.html'

    def form_valid(self, form):
        user = self.request.user
        form.instance.send_from = user
        send_to_username = form.instance.requested_friend_username

        get_user_from_invitation = get_user_model().objects.filter(username=send_to_username)
        if get_user_from_invitation:
            form.instance.send_to = get_user_from_invitation.first()

        return super(InviteCreateView, self).form_valid(form)

    def get_form_kwargs(self):
        """ Passes the request object to the form class.
         This is necessary to only display members that belong to a given user"""

        kwargs = super(InviteCreateView, self).get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs


class InviteListView(LoginRequiredMixin, ListView):
    model = Invite
    template_name = 'friends/invites_list.html'
    context_object_name = 'invites'
    allow_empty = 1

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(Q(send_from=user) | Q(send_to=user))
        return queryset


class InviteChangeStatus(LoginRequiredMixin, views.View):

    def get(self, request, send_from, response):
        user = request.user
        invite = get_object_or_404(Invite, send_to_id=user.id, send_from_id=send_from)
        if response == 1:
            friend = get_user_model().objects.get(id=send_from)
            UserFriend.objects.create(user=user, friend=friend)
            UserFriend.objects.create(user=friend, friend=user)

        if response in [0, 1]:
            invite.delete()

        return redirect('friends:invites_list')


#
class InviteDeleteView(LoginRequiredMixin, views.View):
    def post(self, request):
        user = request.user
        pk = request.POST.get('pk')
        invite = get_object_or_404(Invite, send_from=user, id=pk)
        invite.delete()
        return redirect(reverse_lazy('friends:invites_list'))

class FriendsListView(LoginRequiredMixin, ListView):
    model = UserFriend
    template_name = 'friends/friends_list.html'
