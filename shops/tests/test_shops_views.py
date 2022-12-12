from django.urls import reverse

from categories.models import Category
from conftest import create_fake_shop
from shops.models import Shop


def test_shop_loaded(client, user):
    client.force_login(user)

    endpoint = reverse('shops:list')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert 'Shops' in response.content.decode('UTF-8')


def test_shops_redirect_without_logged_user(client):
    endpoint = reverse('shops:list')
    response = client.get(endpoint)

    assert response.status_code == 302


def test_add_shop(client, user, prepare_fake_categories, faker):
    client.force_login(user)
    categories = Category.objects.all().values_list('id', flat=True)
    input_parameters = {
        'name': faker.word(),
        'is_favourite': faker.boolean(),
        'categories': categories,
    }
    endpoint = reverse('shops:create')

    shops_before_add = Shop.objects.count()
    client.post(endpoint, input_parameters)
    shops_after_add = Shop.objects.count()

    first_shop = Shop.objects.first()

    assert shops_after_add == shops_before_add + 1
    assert first_shop.name == input_parameters['name']


def test_update_category(client, user, prepare_fake_categories, faker):
    client.force_login(user)

    create_fake_shop(user, faker, 1)

    shop = Shop.objects.first()
    shop_new_name = shop.name + '1'

    endpoint = reverse('shops:update', args=[shop.slug])
    input_parameters = {
        'name': shop_new_name,
        'is_favourite': shop.is_favourite,
        'categories': shop.shopcategory_set.all().values_list('id', flat=True),
    }

    response = client.post(endpoint, input_parameters)

    assert response.status_code == 302

    shop.refresh_from_db()
    assert shop.name == shop_new_name


def test_delete_shop_confirmation(client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker, 1)

    assert Shop.objects.first()
    shop = Shop.objects.first()

    endpoint = reverse('shops:delete', args=[shop.slug])
    response = client.get(endpoint)

    assert response.status_code == 200


def test_delete_shop(client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker, 1)

    assert Shop.objects.first()
    shop = Shop.objects.first()

    endpoint = reverse('shops:delete', args=[shop.slug])
    response = client.post(endpoint)

    assert response.status_code == 302
    assert not Shop.objects.filter(id=shop.id)
