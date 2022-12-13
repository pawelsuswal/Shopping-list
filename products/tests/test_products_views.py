from django.urls import reverse

from products.forms import CreateProductForm
from products.models import Product
from testutils import assert_view_get_without_user, create_fake_products


def test_create_product_get(client, user):
    client.force_login(user)
    endpoint = reverse('products:create')
    response = client.get(endpoint)
    assert response.status_code == 200
    form_in_view = response.context['form']
    assert isinstance(form_in_view, CreateProductForm)


def test_create_product_get_without_user(client):
    endpoint = reverse('products:create')
    assert_view_get_without_user(client, endpoint)


def test_create_product_post(db, client, user, faker):
    client.force_login(user)
    create_fake_products(user, faker, 3)
    # category_id = Product.objects.first().id
    input_parameters = {
        'name': 'aaa'
    }
    endpoint = reverse('products:create')

    response = client.post(endpoint, input_parameters)

    assert response.status_code == 302
    assert Product.objects.get(name='aaa')


def test_update_product_get(db, client, user, faker):
    client.force_login(user)
    create_fake_products(user, faker, 3)
    product = Product.objects.first()
    endpoint = reverse('products:update', args=[product.slug])
    response = client.get(endpoint)
    assert response.status_code == 200
    form_in_view = response.context['form']
    assert isinstance(form_in_view, CreateProductForm)


def test_update_product_get_without_user(db, client, user, faker):
    create_fake_products(user, faker, 3)
    product = Product.objects.first()
    endpoint = reverse('products:update', args=[product.slug])
    assert_view_get_without_user(client, endpoint)


def test_update_product_post(db, client, user, faker):
    client.force_login(user)
    create_fake_products(user, faker, 3)
    product = Product.objects.first()
    # category_id = Product.objects.first().id
    input_parameters = {
        'name': 'aaa'
    }
    endpoint = reverse('products:update', args=[product.slug])

    response = client.post(endpoint, input_parameters)

    assert response.status_code == 302
    assert Product.objects.get(name='aaa')


def test_delete_product_get(client, user, faker):
    client.force_login(user)

    create_fake_products(user, faker, 1)
    product = Product.objects.first()

    endpoint = reverse('products:delete', args=[product.slug])
    response = client.get(endpoint)

    assert response.status_code == 200


def test_delete_product_get_without_user(client, user, faker):
    create_fake_products(user, faker, 1)
    product = Product.objects.first()
    endpoint = reverse('products:delete', args=[product.slug])
    assert_view_get_without_user(client, endpoint)


def test_delete_product_post(client, user, faker):
    client.force_login(user)

    create_fake_products(user, faker, 1)

    assert Product.objects.first()
    product = Product.objects.first()

    endpoint = reverse('products:delete', args=[product.slug])
    response = client.post(endpoint)

    assert response.status_code == 302
    assert not Product.objects.filter(id=product.id)


def test_products_list_get(client, user, faker):
    client.force_login(user)
    create_fake_products(user, faker, 2)

    endpoint = reverse('products:list')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['products']
    assert response.context['categories_for_favourite_products']
    assert response.context['categories_for_not_favourite_products']


def test_products_list_get_without_user(client):
    endpoint = reverse('products:list')
    assert_view_get_without_user(client, endpoint)