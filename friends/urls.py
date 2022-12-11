from django.urls import path

from . import views

app_name = 'friends'

urlpatterns = [
    path('invite/', views.InviteCreateView.as_view(), name='create_invite'),
    path('list/', views.FriendsListView.as_view(), name='friends_list'),
    path('invite/list/', views.InviteListView.as_view(), name='invites_list'),
    path('invite/delete/', views.InviteDeleteView.as_view(), name='delete_invite'),

    path('invite/decision/<int:send_from>/<int:response>', views.InviteChangeStatus.as_view(), name='invite_response'),



]
