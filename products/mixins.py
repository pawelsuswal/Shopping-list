import itertools


class ProductMixins:
    def get_categories_by_favourite(self, all_products):
        """Return 2 lists of categories - one for favourite products and second for not favourites one"""
        categories_for_favourite_products = all_products.filter(is_favourite=True).values_list('category__name')
        categories_for_favourite_products = set(categories_for_favourite_products)
        categories_for_favourite_products = list(itertools.chain(*categories_for_favourite_products))

        categories_for_not_favourite_products = all_products.filter(is_favourite=False).values_list('category__name')
        categories_for_not_favourite_products = set(categories_for_not_favourite_products)
        categories_for_not_favourite_products = list(itertools.chain(*categories_for_not_favourite_products))

        if None in categories_for_favourite_products:
            categories_for_favourite_products[categories_for_favourite_products.index(None)] = ''

        if None in categories_for_not_favourite_products:
            categories_for_not_favourite_products[categories_for_not_favourite_products.index(None)] = ''

        categories_for_favourite_products.sort()
        categories_for_not_favourite_products.sort()
        return categories_for_favourite_products, categories_for_not_favourite_products
