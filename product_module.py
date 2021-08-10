class Product:
    def __init__(self, supplier, product_name, product_info_dict):
        self.suppler = supplier
        self.product_name = product_name
        self.product_info_dict = product_info_dict

    def toArray(self, attributesToInclude):
        result = []
        for attribute in attributesToInclude:
            attribute_value = ""

            if attribute in self.product_info_dict:
                attribute_value = self.product_info_dict[attribute]

            result.append(attribute_value)

        return result
