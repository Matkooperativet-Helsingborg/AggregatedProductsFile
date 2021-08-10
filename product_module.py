class Product:
    def __init__(self, supplier, product_name, product_info_dict):
        self.supplier = supplier
        self.product_name = product_name
        self.product_info_dict = product_info_dict

    def toArrayIncludingSupplier(self, attributesToInclude):
        result = [self.supplier]
        for attribute in attributesToInclude:
            attribute_value = ""

            if attribute in self.product_info_dict:
                attribute_value = self.product_info_dict[attribute]

            result.append(attribute_value)

        return result
