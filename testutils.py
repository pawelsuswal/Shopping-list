from django.urls import reverse
from django.utils.text import slugify

from categories.models import Category
from products.models import Product, UNITS_OF_MEASUREMENT
from shopping_list.models import ShoppingList
from shops.models import Shop
from random import sample, randint


def assert_view_get_without_user(client, endpoint):
    response = client.get(endpoint)

    assert response.status_code == 302
    assert response.url.startswith(reverse('login'))


def create_fake_categories(user, faker, count=1):
    for _ in range(1, count + 1):
        Category.objects.create(**{
            'name': faker.word(),
            'user': user,
            'is_favourite': faker.boolean()
        })


def create_fake_shop(user, faker, count=1):
    categories_count = 10
    create_fake_categories(user, faker, count=categories_count)
    categories_id = list(Category.objects.all().values_list('id', flat=True))

    for _ in range(1, count + 1):
        categories = sample(categories_id, k=randint(0, categories_count))
        shop = Shop.objects.create(**{
            'name': faker.word(),
            'user': user,
            'is_favourite': faker.boolean(),
        })
        for count, category in enumerate(categories):
            shop.shopcategory_set.create(category_id=category, order=count)


def create_fake_products(user, faker, count=1, create_categories=True):
    uom_count = len(UNITS_OF_MEASUREMENT) - 1
    if create_categories:
        create_fake_categories(user, faker, 10)
    categories_id = list(Category.objects.all().values_list('id', flat=True))
    for counter in range(1, count + 1):
        uom = UNITS_OF_MEASUREMENT[uom_count % counter][0]
        is_favourite = bool(counter % 2)
        category_id = categories_id[(len(categories_id) - 1) % counter]
        Product.objects.create(
            name=f'Product {counter}',
            user=user,
            category_id=category_id,
            is_favourite=is_favourite,
            default_amount=counter,
            default_uom=uom
        )


def create_fake_shopping_lists(user, faker, count=1, favourite=False, finished=False, shops_count=1):
    create_fake_shop(user, faker, shops_count)
    shops_ids = list(Shop.objects.order_by('id').values_list('id', flat=True))
    is_favourite = False
    is_finished = False
    for counter in range(1, count + 1):
        shop_id = shops_ids[(len(shops_ids) - 1) % counter]
        if favourite:
            is_favourite = not is_favourite
        if finished:
            is_finished = not is_finished
        shopping_list = ShoppingList.objects.create(
            name=f'Shopping list + {counter}',
            is_finished=is_finished,
            is_favourite=is_favourite,
            user=user,
            shop_id=shop_id,
        )
        user_id = str(shopping_list.user_id)
        shopping_list_id = str(shopping_list.id)
        shopping_list.slug = slugify('-'.join((user_id, shopping_list_id)))
        shopping_list.save()


def add_products_to_shopping_list(shopping_list: ShoppingList, user, faker, count=1, bought=False, amount=False,
                                  uom=False,
                                  comment=False):
    create_fake_products(user, faker, create_categories=False)
    products_ids = list(Product.objects.order_by('id').values_list('id', flat=True))
    is_bought = False
    uom_count = len(UNITS_OF_MEASUREMENT) - 1

    for counter in range(1, count + 1):
        product_id = products_ids[(len(products_ids) - 1) % counter]
        if bought:
            is_bought = not is_bought

        if amount:
            amount_to_save = counter
        else:
            amount_to_save = Product.objects.get(id=product_id).default_amount

        if uom:
            uom_to_save = UNITS_OF_MEASUREMENT[uom_count % counter][0]
        else:
            uom_to_save = Product.objects.get(id=product_id).default_uom

        if comment:
            comment_to_save = f'Comment {counter}'
        else:
            comment_to_save = ''

        shopping_list.productshoppinglist_set.create(
            product_id=product_id,
            is_bought=is_bought,
            amount=amount_to_save,
            unit_of_measurement=uom_to_save,
            comment=comment_to_save,
        )
