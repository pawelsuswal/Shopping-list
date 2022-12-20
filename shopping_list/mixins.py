from django.core.exceptions import ObjectDoesNotExist

from products.mixins import ProductMixins
from products.models import Product, UNITS_OF_MEASUREMENT
from shopping_list.models import ShoppingList, ProductShoppingList


class ShoppingListMixins(ProductMixins):
    def get_all_products(self, user, shopping_list=None):
        """Returns list of all products split by favourites and categories for
         selected user with current values from shopping list if provided"""
        all_products = Product.objects.filter(user=user).order_by('-is_favourite', 'name')
        categories_for_favourite_products, categories_for_not_favourite_products = self.get_categories_by_favourite(
            all_products)

        products_by_categories_and_favourites = [[True, []], [False, []]]

        for data_set in products_by_categories_and_favourites:
            is_favourite = data_set[0]

            if is_favourite:
                category_set = categories_for_favourite_products
            else:
                category_set = categories_for_not_favourite_products

            for category in category_set:
                if category == '':
                    category = None

                products_for_category = all_products.filter(category__name=category,
                                                            is_favourite=is_favourite).order_by(
                    'name')

                products_to_save = []

                for product in products_for_category:
                    if shopping_list and product in shopping_list.products.all():
                        product_from_shopping_list = shopping_list.productshoppinglist_set.get(product=product)
                        product_to_save = {
                            'id': product.id,
                            'checked': True,
                            'name': product.name,
                            'amount': product_from_shopping_list.amount,
                            'uom': product_from_shopping_list.unit_of_measurement,
                            'comment': product_from_shopping_list.comment,
                        }

                    else:
                        product_to_save = {
                            'id': product.id,
                            'checked': False,
                            'name': product.name,
                            'amount': product.default_amount,
                            'uom': product.default_uom,
                            'comment': '',
                        }

                    products_to_save.append(product_to_save)

                if products_to_save:
                    data_set[1].append([category, products_to_save])

        return products_by_categories_and_favourites

    def get_products_for_shopping_list(self, user, post_data):
        """Return list of product with parameters provided in post_data"""
        products_for_shopping_list = []

        for item in post_data.items():
            if 'product' not in item[0]:
                continue

            product_id = int(item[0].split('-id-')[1])
            product = Product.objects.filter(user=user, id=product_id)

            if not product:
                raise ObjectDoesNotExist

            product = product.first()
            product_id = str(product_id)
            amount = post_data[''.join(('amount-id-', product_id))]
            uom = post_data[''.join(('uom-id-', product_id))]
            comment = post_data[''.join(('comment-id-', product_id))]

            if amount == '':
                amount = None
            else:
                amount = float(amount)

            if not any(uom in uom_code for uom_code in UNITS_OF_MEASUREMENT) and uom != 'None':
                raise ValueError

            if uom == 'None' or uom == '':
                uom = None

            products_for_shopping_list.append({
                'product': product,
                'amount': amount,
                'uom': uom,
                'comment': comment,
            })
        return products_for_shopping_list

    def save_products_in_shopping_list(self, products_to_save, shopping_list):
        """Saves products for shopping list in database"""
        for product_to_save in products_to_save:
            shopping_list.productshoppinglist_set.update_or_create(
                product=product_to_save['product'],
                defaults={
                    'amount': product_to_save['amount'],
                    'unit_of_measurement': product_to_save['uom'],
                    'comment': product_to_save['comment'],
                }
            )

    def clear_products_in_shopping_list(self, shopping_list: ShoppingList):
        """Removes all products from shopping list"""
        for product in shopping_list.productshoppinglist_set.all():
            product.delete()

    def get_shopping_lists(self, shopping_lists, user=None):
        """Returns list of shopping lists with products related to each of them ordered by category"""
        uom = dict(UNITS_OF_MEASUREMENT)
        data_to_render = []
        for shopping_list in shopping_lists:
            products = []
            if shopping_list.shop is None:
                products_query_set = shopping_list.productshoppinglist_set.all().order_by('product__name')
                for product in products_query_set.all():
                    if product.amount is None:
                        product.amount = ''
                    if product.unit_of_measurement is not None:
                        product.unit_of_measurement = uom[product.unit_of_measurement]
                    products.append(product)

            else:
                products = ProductShoppingList.objects.raw(
                    '''select * from shopping_list_productshoppinglist as psl 
                    left join products_product as p on p.id = psl.product_id
                    left join shops_shopcategory as sc on (p.category_id = sc.category_id and sc.shop_id = %s )
                    where shopping_list_id = %s
                    ''',
                    [shopping_list.shop_id, shopping_list.id])
                products = [item for item in products]

                for product in products:
                    if product.order is None:
                        product.order = -1
                    if product.amount is None:
                        product.amount = ''
                    if product.unit_of_measurement is not None:
                        product.unit_of_measurement = uom[product.unit_of_measurement]

                products = sorted(products, key=lambda x: (x.order, x.product.name,))

            shared = False
            if user is not None and shopping_list.user != user:
                shared = True

            data_to_render.append([shopping_list, products, shared])
        return data_to_render
