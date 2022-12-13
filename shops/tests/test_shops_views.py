from django.urls import reverse

from categories.models import Category
from testutils import create_fake_shop, create_fake_categories
from shops.forms import CreateShopForm
from shops.models import Shop
from testutils import assert_view_get_without_user


def test_create_shop_get(client, user):
    client.force_login(user)
    endpoint = reverse('shops:create')
    response = client.get(endpoint)
    assert response.status_code == 200
    form_in_view = response.context['form']
    assert isinstance(form_in_view, CreateShopForm)


def test_create_shop_get_without_user(client):
    endpoint = reverse('shops:create')
    assert_view_get_without_user(client, endpoint)


def test_create_shop_post(db, client, user, faker):
    client.force_login(user)
    create_fake_categories(user, faker, 3)
    category_id = Category.objects.first().id
    input_parameters = {
        'name': 'aaa',
        'is_favourite': True,
        'categories': category_id,
    }
    endpoint = reverse('shops:create')

    response = client.post(endpoint, input_parameters)

    assert response.status_code == 302
    assert Shop.objects.get(name='aaa')


def test_update_shop_get_without_user(client, user, faker):
    create_fake_shop(user, faker, 1)
    shop = Shop.objects.first()
    endpoint = reverse('shops:update', args=[shop.slug])
    assert_view_get_without_user(client, endpoint)


def test_update_shop_post(client, user, faker):
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


def test_delete_shop_get(client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker, 1)
    shop = Shop.objects.first()

    endpoint = reverse('shops:delete', args=[shop.slug])
    response = client.get(endpoint)

    assert response.status_code == 200


def test_delete_shop_get_without_user(client, user, faker):
    create_fake_shop(user, faker, 1)
    shop = Shop.objects.first()
    endpoint = reverse('shops:delete', args=[shop.slug])
    assert_view_get_without_user(client, endpoint)


def test_delete_shop_post(client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker, 1)

    assert Shop.objects.first()
    shop = Shop.objects.first()

    endpoint = reverse('shops:delete', args=[shop.slug])
    response = client.post(endpoint)

    assert response.status_code == 302
    assert not Shop.objects.filter(id=shop.id)


def test_shops_list_get(client, user, faker):
    client.force_login(user)
    create_fake_shop(user, faker, 1)

    endpoint = reverse('shops:list')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['shops']


def test_shops_list_get_without_user(client):
    endpoint = reverse('shops:list')
    assert_view_get_without_user(client, endpoint)


def test_shops_reorder_categories_get(db, client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker)
    shop = Shop.objects.first()

    endpoint = reverse('shops:reorder', args=[shop.slug])
    response = client.get(endpoint)

    assert response.status_code == 200
    shop_categories = response.context['shop_categories']
    assert shop_categories

    endpoint_for_change_order = reverse('shops:reorder', args=[
        shop_categories.first().shop.slug,
        shop_categories.first().category_id,
    ])
    assert endpoint_for_change_order in response.content.decode('UTF-8')


def test_shops_reorder_categories_get_without_user(client, user, faker):
    create_fake_shop(user, faker)
    shop = Shop.objects.first()

    endpoint = reverse('shops:reorder', args=[shop.slug])
    assert_view_get_without_user(client, endpoint)


def test_shops_reorder_categories_post_up(db, client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker)
    shop = Shop.objects.first()
    shop_category = shop.shopcategory_set.last()

    endpoint = reverse('shops:reorder', args=[
        shop.slug,
        shop_category.category_id,
    ])

    shop_category_order_before_change = shop_category.order

    response = client.post(endpoint, {'up': ''})

    assert response.status_code == 302

    shop_category.refresh_from_db()

    assert shop_category_order_before_change - 1 == shop_category.order


def test_shops_reorder_categories_post_down(db, client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker)
    shop = Shop.objects.first()
    shop_category = shop.shopcategory_set.first()

    endpoint = reverse('shops:reorder', args=[
        shop.slug,
        shop_category.category_id,
    ])

    shop_category_order_before_change = shop_category.order

    response = client.post(endpoint, {'down': ''})

    assert response.status_code == 302

    shop_category.refresh_from_db()

    assert shop_category_order_before_change + 1 == shop_category.order


def test_shops_reorder_categories_post_top(db, client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker)
    shop = Shop.objects.first()
    shop_category = shop.shopcategory_set.last()

    endpoint = reverse('shops:reorder', args=[
        shop.slug,
        shop_category.category_id,
    ])

    response = client.post(endpoint, {'top': ''})

    assert response.status_code == 302

    shop_category.refresh_from_db()

    assert shop_category.order == 0


def test_shops_reorder_categories_post_bottom(db, client, user, faker):
    client.force_login(user)

    create_fake_shop(user, faker)
    shop = Shop.objects.first()
    shop_category = shop.shopcategory_set.first()

    endpoint = reverse('shops:reorder', args=[
        shop.slug,
        shop_category.category_id,
    ])

    response = client.post(endpoint, {'bottom': ''})

    assert response.status_code == 302

    shop_category.refresh_from_db()

    assert shop_category.order == shop.shopcategory_set.count() - 1
