from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.CreateUserView.as_view(), name='signup')
    
]
