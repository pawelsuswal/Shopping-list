from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView
from django import views

from friends.forms import InviteCreateForm
from friends.models import UserFriend, Invite


class InviteCreateView(LoginRequiredMixin, CreateView):
    """Display view for create new invite"""
    model = Invite
    form_class = InviteCreateForm
    success_url = reverse_lazy('friends:friends_list')
    template_name = 'friends/create_invite.html'

    def form_valid(self, form):
        """Check if user with requested username exist and save it"""
        user = self.request.user
        form.instance.send_from = user
        send_to_username = form.cleaned_data['requested_friend_username']

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
    """Display view with send and received invites"""
    model = Invite
    template_name = 'friends/invites_list.html'
    context_object_name = 'invites'
    allow_empty = 1

    def get_queryset(self):
        """Setup queryset for only send and received invites of current user"""
        queryset = super().get_queryset()
        user = self.request.user
        queryset = queryset.filter(Q(send_from=user) | Q(send_to=user))
        return queryset


class InviteChangeStatus(LoginRequiredMixin, views.View):
    """Handle user accept or decline invite action"""

    def post(self, request, send_from, response):
        """Check if invite exist, resolve user decision and remove invite"""
        user = request.user
        invite = get_object_or_404(Invite, send_to_id=user.id, send_from_id=send_from)
        if response == 1:
            friend = get_user_model().objects.get(id=send_from)
            UserFriend.objects.create(user=user, friend=friend)
            UserFriend.objects.create(user=friend, friend=user)
            revert_invite = Invite.objects.filter(send_to_id=send_from, send_from_id=user.id)
            if revert_invite.exists():
                revert_invite.delete()

        if response in [0, 1]:
            invite.delete()

        return redirect('friends:invites_list')


#
class InviteDeleteView(LoginRequiredMixin, views.View):
    """Handle delete invite request"""

    def post(self, request):
        """Check if invite from current user for selected pk exist and remove it if so"""
        user = request.user
        pk = request.POST.get('pk')
        invite = get_object_or_404(Invite, send_from=user, id=pk)
        invite.delete()
        return redirect(reverse_lazy('friends:invites_list'))


class FriendsListView(LoginRequiredMixin, ListView):
    """Show view with friends list for current user"""
    model = UserFriend
    template_name = 'friends/friends_list.html'
    context_object_name = 'friends'

    def get_queryset(self):
        """Setup queryset to pick friends only for current user"""
        query_set = super(FriendsListView, self).get_queryset()
        query_set = query_set.filter(user=self.request.user)
        return query_set


class FriendDeleteView(LoginRequiredMixin, views.View):
    """Handle delete friend request"""

    def post(self, request):
        """Check if there is relation between current user and selected friend and delete it if so"""
        user_id = request.user.id
        friend_id = request.POST.get('pk')

        friend = UserFriend.objects.filter(user_id=user_id, friend_id=friend_id)
        friend_reverse = UserFriend.objects.filter(user_id=friend_id, friend_id=user_id)
        if not friend and not friend_reverse:
            return HttpResponseNotFound('No object found')
        if friend:
            friend.first().delete()
        if friend_reverse:
            friend_reverse.first().delete()

        return redirect(reverse_lazy('friends:friends_list'))
