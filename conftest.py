import pytest

from categories.models import Category
from shops.models import Shop
from random import sample, randint


@pytest.fixture()
def user(db, django_user_model, faker):
    """ Create django user"""
    return django_user_model.objects.create(email=faker.name(),
                                            username=faker.user_name(),
                                            password=faker.password(length=10, special_chars=False))


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


@pytest.fixture
def prepare_fake_categories(user, faker):
    create_fake_categories(user, faker, 3)
