import pytest


@pytest.fixture
def user(db, django_user_model):
    """ Create django user"""
    return django_user_model.objects.create(email='test456@admin.com', username='Test User', password='TestPass123')
