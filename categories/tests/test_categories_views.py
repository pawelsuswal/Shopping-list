from django.urls import reverse
from django.utils.text import slugify

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
    input_params = {
        'name': 'test category',
        'is_favourite': True,
    }
    endpoint = reverse('categories:create')
    # assert creating fresh new category

    before_categories = Category.objects.all().count()

    client.post(endpoint, input_params)

    after_categories = Category.objects.all()
    first_category = after_categories.first()

    assert before_categories + 1 == after_categories.count()
    assert first_category.name == input_params['name']
    assert first_category.is_favourite == input_params['is_favourite']
    assert first_category.is_active is True
    assert first_category.slug == slugify(input_params['name'])
    assert first_category.user == user

    # assert creating category, when one was deleted (deactivated in fact)
    first_category.is_active = False
    first_category.save()

    client.post(endpoint, input_params)
    first_category.refresh_from_db()

    assert first_category.is_active is True


def test_update_category(client, user):
    client.force_login(user)
    category = Category.objects.create(name='category 1', is_favourite=True, user=user)
    link = reverse('categories:update', args=[category.slug])
    new_category_name = 'category 2'

    response = client.post(link, {'name': new_category_name, 'is_favourite': category.is_favourite})

    assert response.status_code == 302

    category.refresh_from_db()
    assert category.name == new_category_name


def test_delete_category(client, user):
    # category should not be truly deleted but deactivated instead
    client.force_login(user)
    category = Category.objects.create(name='category 1', is_favourite=True, user=user)

    assert category.is_active is True

    link = reverse('categories:delete', args=[category.slug])
    client.get(link)

    category.refresh_from_db()
    assert category.is_active is False
