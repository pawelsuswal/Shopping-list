from django.urls import reverse

from categories.models import Category


def test_categories_loaded(client, user):
    client.force_login(user)

    endpoint = reverse('categories:list')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert 'Categories' in response.content.decode('UTF-8')


def test_categories_redirect_without_logged_user(client):
    endpoint = reverse('categories:list')
    response = client.get(endpoint)

    assert response.status_code == 302


def test_add_category(client, user):
    client.force_login(user)
    input_parameters = {
        'name': 'test category',
        'is_favourite': True,
    }
    endpoint = reverse('categories:create')

    before_categories = Category.objects.count()

    client.post(endpoint, input_parameters)

    after_categories = Category.objects.all()
    first_category = after_categories.first()

    assert before_categories + 1 == after_categories.count()
    assert first_category.name == input_parameters['name']
    assert first_category.is_favourite == input_parameters['is_favourite']
    assert first_category.user == user


def test_update_category(client, user):
    client.force_login(user)
    category = Category.objects.create(name='category 1', is_favourite=True, user=user)
    endpoint = reverse('categories:update', args=[category.slug])
    new_category_name = 'category 2'

    response = client.post(endpoint, {'name': new_category_name, 'is_favourite': category.is_favourite})

    assert response.status_code == 302

    category.refresh_from_db()
    assert category.name == new_category_name


def test_delete_category_confirmation(client, user):
    client.force_login(user)
    category = Category.objects.create(name='category 1', is_favourite=True, user=user)

    endpoint = reverse('categories:delete', args=[category.slug])
    response = client.get(endpoint)

    assert response.status_code == 200


def test_delete_category(client, user):
    client.force_login(user)
    category = Category.objects.create(name='category 1', is_favourite=True, user=user)

    endpoint = reverse('categories:delete', args=[category.slug])
    response = client.post(endpoint)

    assert response.status_code == 302
    assert not Category.objects.filter(id=category.id)
