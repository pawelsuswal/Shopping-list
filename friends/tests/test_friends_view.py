from django.db.models import QuerySet
from django.urls import reverse

from friends.forms import InviteCreateForm
from friends.models import Invite, UserFriend
from testutils import assert_view_get_without_user, create_fake_invite_to_existing_user, create_fake_friend


def test_invite_create_get(client, user):
    client.force_login(user)
    endpoint = reverse('friends:create_invite')
    response = client.get(endpoint)

    assert response.status_code == 200

    form_in_view = response.context['form']
    assert isinstance(form_in_view, InviteCreateForm)


def test_invite_create_get_without_user(client, user):
    endpoint = reverse('friends:create_invite')
    assert_view_get_without_user(client, endpoint)


def test_invite_create_post(client, user):
    client.force_login(user)
    endpoint = reverse('friends:create_invite')

    response = client.post(endpoint, {'requested_friend_username': 'aaa'})

    assert response.status_code == 302

    assert Invite.objects.get(requested_friend_username='aaa')


def test_invite_list_get(client, user):
    client.force_login(user)
    endpoint = reverse('friends:invites_list')

    response = client.get(endpoint)

    assert response.status_code == 200

    form_in_view = response.context['invites']
    assert isinstance(form_in_view, QuerySet)


def test_invite_list_get_without_user(client, user):
    endpoint = reverse('friends:invites_list')
    assert_view_get_without_user(client, endpoint)


def test_invite_delete_post(client, user, user2):
    create_fake_invite_to_existing_user(user, user2)

    invite = Invite.objects.first()
    invite_id = invite.id

    client.force_login(user)

    endpoint = reverse('friends:delete_invite')

    response = client.post(endpoint, {'pk': invite_id})

    assert response.status_code == 302

    assert not Invite.objects.filter(id=invite_id)


def test_invite_delete_post_without_user(client, user, user2):
    create_fake_invite_to_existing_user(user, user2)

    endpoint = reverse('friends:delete_invite')
    assert_view_get_without_user(client, endpoint)


def test_invite_response_get(client, user, user2):
    create_fake_invite_to_existing_user(user, user2)
    client.force_login(user2)

    endpoint = reverse('friends:invite_response', args=[
        user.id,
        1,
    ])

    response = client.get(endpoint)

    assert response.status_code == 302

    assert UserFriend.objects.get(user=user, friend=user2)
    assert UserFriend.objects.get(user=user2, friend=user)


def test_invite_response_get_without_user(client, user, user2):
    create_fake_invite_to_existing_user(user, user2)

    endpoint = reverse('friends:invite_response', args=[
        user.id,
        1,
    ])
    assert_view_get_without_user(client, endpoint)


def test_friend_list_get(client, user, user2):
    client.force_login(user)
    create_fake_friend(user, user2)

    endpoint = reverse('friends:friends_list')

    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['friends']


def test_friend_list_get_without_user(client, user, user2):
    create_fake_friend(user, user2)

    endpoint = reverse('friends:friends_list')
    assert_view_get_without_user(client, endpoint)


def test_friend_delete_post(client, user, user2):
    client.force_login(user)
    create_fake_friend(user, user2)

    endpoint = reverse('friends:delete_friend')

    response = client.post(endpoint, {'pk': user2.id})

    assert response.status_code == 302
    assert not UserFriend.objects.filter(user=user, friend=user2)
    assert not UserFriend.objects.filter(user=user2, friend=user)


def test_friend_delete_post_without_user(client, user, user2):

    create_fake_friend(user, user2)

    endpoint = reverse('friends:delete_friend')

    assert_view_get_without_user(client, endpoint)
