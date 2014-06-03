import os
from . import csv_loader
from ..entities import product

def build_products(filepath):
    """ Generates a list of all products by reading in from a csv file"""
    try:
        product_info = csv_loader.load_csv_info(filepath)
        if product_info == None:
            print('No product info.')
            return
        product_list = []
        for row in product_info:
            # the first two rows are junk... this should be done less sloppily later
            if row[0] == '' or row[1] == '' or row[2] == '': 
                #all products should have these fields
                continue
            # according to the excel formatting
            product_code = row[0]
            product_name = row[1]
            family_group = row[2]
            viscosity_range = [row[3],row[4], row[5]] # low, high and type
            density = row[6]
            viscosity_specs_at_40 = [row[7], row[8], row[9]]
            viscosity_specs_at_100 = [row[10], row[11], row[12]]
            sensitivity = row[13]
            p = product.Product(product_code, product_name, family_group, density, viscosity_range, viscosity_specs_at_40, viscosity_specs_at_100, sensitivity)
            product_list.append(p)
            print (p)
        return product_list
    except ValueError as e:
        if e is ValueError:
            pass
        else :
            print ("An error occurred when trying to build product list from file " + os.path.basename(filepath))
            return None


