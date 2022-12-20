from django.urls import reverse

from shopping_list.forms import CreateShoppingListForm
from shopping_list.models import ShoppingList
from testutils import assert_view_get_without_user, create_fake_products, create_fake_shopping_lists, \
    add_products_to_shopping_list


def test_create_shopping_list_get(client, user, faker):
    """Check if view for create new shoppping list is loading"""
    client.force_login(user)
    create_fake_products(user, faker, 5)
    endpoint = reverse('shopping_list:create')
    response = client.get(endpoint)
    assert response.status_code == 200
    form_in_view = response.context['form']
    assert isinstance(form_in_view, CreateShoppingListForm)
    assert response.context['products_by_categories_and_favourites']
    assert response.context['UNITS_OF_MEASUREMENT']


def test_create_shopping_list_get_without_user(client):
    """Check if page for create new shopping list is redirecting not logged user to login page"""
    endpoint = reverse('shopping_list:create')
    assert_view_get_without_user(client, endpoint)


def test_create_shopping_list_post(db, client, user, faker):
    """Check if shopping list is created on post method"""
    client.force_login(user)

    input_parameters = {
        'name': 'aaa',
        'user': user,
    }
    endpoint = reverse('shopping_list:create')

    response = client.post(endpoint, input_parameters)

    assert response.status_code == 302
    assert ShoppingList.objects.get(name='aaa')


def test_update_shopping_list_get(db, client, user, faker):
    """Check if view for update existing new shoppping list is loading"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker)

    shopping_list = ShoppingList.objects.first()

    endpoint = reverse('shopping_list:update', args=[shopping_list.slug])
    response = client.get(endpoint)
    assert response.status_code == 200
    form_in_view = response.context['form']
    assert isinstance(form_in_view, CreateShoppingListForm)


def test_update_shopping_list_get_without_user(db, client, user, faker):
    """Check if page for update existing shopping list is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker)

    shopping_list = ShoppingList.objects.first()

    endpoint = reverse('shopping_list:update', args=[shopping_list.slug])
    assert_view_get_without_user(client, endpoint)


def test_update_shopping_list_post(db, client, user, faker):
    """Check if shopping list is updated on post method"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()

    input_parameters = {
        'name': 'aaa'
    }
    endpoint = reverse('shopping_list:update', args=[shopping_list.slug])

    response = client.post(endpoint, input_parameters)

    assert response.status_code == 302
    assert ShoppingList.objects.get(name='aaa')


def test_delete_shopping_list_get(client, user, faker):
    """Check if view for delete existing shopping list is loading confirmation page"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker, 1)
    shopping_list = ShoppingList.objects.first()

    endpoint = reverse('shopping_list:delete', args=[shopping_list.slug])
    response = client.get(endpoint)

    assert response.status_code == 200


def test_delete_shopping_list_get_without_user(client, user, faker):
    """Check if delete request is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker, 1)
    shopping_list = ShoppingList.objects.first()
    endpoint = reverse('shopping_list:delete', args=[shopping_list.slug])
    assert_view_get_without_user(client, endpoint)


def test_delete_shopping_list_post(client, user, faker):
    """Check if shopping list is deleted on post method"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker, 1)

    assert ShoppingList.objects.first()
    shopping_list = ShoppingList.objects.first()

    endpoint = reverse('shopping_list:delete', args=[shopping_list.slug])
    response = client.post(endpoint)

    assert response.status_code == 302
    assert not ShoppingList.objects.filter(id=shopping_list.id)


def test_shopping_list_list_get(client, user, faker):
    """Check if view for list of shopping lists is loading"""
    client.force_login(user)
    create_fake_shopping_lists(user, faker)

    endpoint = reverse('shopping_list:list')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['data_to_render']


def test_shopping_list_list_get_without_user(client, user, faker):
    """Check if view for list of shopping lists is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker)

    endpoint = reverse('shopping_list:list')

    assert_view_get_without_user(client, endpoint)


def test_update_product_status(client, user, faker):
    """Check if user request is changing product status in shopping list to opposite"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()
    add_products_to_shopping_list(shopping_list, user, faker)

    product = shopping_list.productshoppinglist_set.first()

    product_status_before_update = product.is_bought
    endpoint = reverse('shopping_list:change_product_status', args=[shopping_list.slug, product.id])
    response = client.post(endpoint)

    assert response.status_code == 302
    product.refresh_from_db()
    assert product_status_before_update != product.is_bought


def test_update_product_status_without_user(client, user, faker):
    """Check if view for change product status is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()
    add_products_to_shopping_list(shopping_list, user, faker)

    product = shopping_list.productshoppinglist_set.first()

    endpoint = reverse('shopping_list:change_product_status', args=[shopping_list.slug, product.id])
    response = client.post(endpoint)

    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))


def test_comment_view_get(client, user, faker):
    """Check if view for show comment for selected product in shopping list is loading"""

    client.force_login(user)

    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()
    add_products_to_shopping_list(shopping_list, user, faker, comment=True)

    product = shopping_list.productshoppinglist_set.first()

    endpoint = reverse('shopping_list:view_comment', args=[shopping_list.slug, product.id])
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['product']


def test_comment_view_get_without_user(client, user, faker):
    """Check if view for show comment is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()
    add_products_to_shopping_list(shopping_list, user, faker, comment=True)

    product = shopping_list.productshoppinglist_set.first()

    endpoint = reverse('shopping_list:view_comment', args=[shopping_list.slug, product.id])
    assert_view_get_without_user(client, endpoint)


def test_comment_view_post(client, user, faker):
    """Check if post method of view comment is redirecting to previous view of one of the shopping lists groups"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()
    add_products_to_shopping_list(shopping_list, user, faker, comment=True)

    product = shopping_list.productshoppinglist_set.first()
    endpoint = reverse('shopping_list:view_comment', args=[shopping_list.slug, product.id])

    previous = reverse('shopping_list:list')

    response = client.post(endpoint, {'previous': previous})

    assert response.status_code == 302
    assert response.url.startswith(previous)


def test_update_shopping_list_status_post(client, user, faker):
    """Check if user request is changing shopping list status to opposite"""
    client.force_login(user)

    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()

    assert not shopping_list.is_finished

    shopping_list_status_before_update = shopping_list.is_finished

    endpoint = reverse('shopping_list:change_finish_status', args=[shopping_list.slug])
    response = client.post(endpoint)

    assert response.status_code == 302
    shopping_list.refresh_from_db()
    assert shopping_list_status_before_update != shopping_list.is_finished


def test_update_shopping_list_status_without_user(client, user, faker):
    """Check if view for change shopping list status is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker)
    shopping_list = ShoppingList.objects.first()

    endpoint = reverse('shopping_list:change_finish_status', args=[shopping_list.slug])
    assert_view_get_without_user(client, endpoint)


def test_shopping_list_history_view(client, user, faker):
    """Check if view for list of finished shopping lists is loading"""
    client.force_login(user)
    create_fake_shopping_lists(user, faker, finished=True)

    endpoint = reverse('shopping_list:history')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['data_to_render']


def test_shopping_list_history_view_without_user(client, user, faker):
    """Check if view for list of finished shopping lists is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker, finished=True)

    endpoint = reverse('shopping_list:history')

    assert_view_get_without_user(client, endpoint)


def test_shopping_list_favourite_view(client, user, faker):
    """Check if view for list of favourite shopping lists is loading"""
    client.force_login(user)
    create_fake_shopping_lists(user, faker, favourite=True)

    endpoint = reverse('shopping_list:favourites')
    response = client.get(endpoint)

    assert response.status_code == 200
    assert response.context['data_to_render']


def test_shopping_list_favourite_view_without_user(client, user, faker):
    """Check if view for list of favourite shopping lists is redirecting not logged user to login page"""
    create_fake_shopping_lists(user, faker, favourite=True)

    endpoint = reverse('shopping_list:favourites')

    assert_view_get_without_user(client, endpoint)
