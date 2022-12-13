from django.urls import reverse


def test_home_view_get(client, user):
    client.force_login(user)
    endpoint = reverse('home:home')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert 'Welcome to shopping list app' in response.content.decode('UTF-8')
    assert 'Please login to access all features!' not in response.content.decode('UTF-8')

def test_home_view_get_without_user(client):
    endpoint = reverse('home:home')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert 'Welcome to shopping list app' in response.content.decode('UTF-8')
    assert 'Please login to access all features!' in response.content.decode('UTF-8')