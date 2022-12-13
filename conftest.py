import pytest



@pytest.fixture()
def user(db, django_user_model, faker):
    """ Create django user"""
    return django_user_model.objects.create(email=faker.name(),
                                            username=faker.user_name(),
                                            password=faker.password(length=10, special_chars=False))





# @pytest.fixture
# def prepare_fake_categories(user, faker):
#     create_fake_categories(user, faker, 3)
#
#
# @pytest.fixture
# def prepare_fake_product(user, faker):
#     create_fake_products(user, faker)


# @pytest.fixture
# def prepare_fake_products(user):
#     create_fake_products(user, 10)
