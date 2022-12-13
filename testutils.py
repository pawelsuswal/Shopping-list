from django.urls import reverse
from categories.models import Category
from products.models import Product, UNITS_OF_MEASUREMENT
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


def create_fake_products(user, faker, count=1):
    uom_count = len(UNITS_OF_MEASUREMENT) - 1
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
