import os
from . import csv_loader
from ..entities import product

global list_of_elements
list_of_elements = [ 'Barium',
                     'Calcium',
                     'Copper',
                     'Chromium',
                     'Iron',
                     'Lead',
                     'Nickel',
                     'Nitrogen',
                     'Molybdenum',
                     'Silicon',
                     'Silver',
                     'Sulphur',
                     'Tin',
                     'Titanium',
                     'Magnesium',
                     'Phosphorus',
                     'Zinc',
                    ]

def assign_elemental_values(product):
    global elemental_info
    global material_code_column
    global elemental_value_column
    global elemental_description_column
    element_dictionary= {}

    # find first index of the products' material code in the elemental info array
    first_index = None
    for row in elemental_info:
        if str(product.material_code) not in row[material_code_column]:
           continue 
        first_index = elemental_info.index(row)
        break
    if first_index is None:
        print("No information found for product "+product.name)
        return None
    initial_row = elemental_info[first_index]
    curr_row = initial_row
    curr_index = first_index
    # check each row for elemental values
    while str(product.material_code) in curr_row[material_code_column]:
        # add elemental value if it exists
        global list_of_elements
        for e in list_of_elements:
            
            if e.lower() in curr_row[elemental_description_column].lower():
                print("Match found")
                element_dictionary[e] = row[elemental_value_column]
        curr_index += 1
        curr_row = elemental_info[curr_index]
    product.elemental_values = element_dictionary

def load_elemental_info(elemental_filepath):
    global elemental_info 
    elemental_info = csv_loader.load_csv_info(elemental_filepath)
    header_row = elemental_info[0] # this is a 2D array, so the first element is the first row
    # determine locations of relevant columns based on SAP naming conventions
    global elemental_description_column
    global material_code_column
    global elemental_value_column
    for h in header_row:
        if h is None or h == '':
            continue
        if h.lower() == 'MIC description'.lower():
            elemental_description_column = header_row.index(h)
        if h.lower() == 'Material'.lower():
            material_code_column = header_row.index(h)
        if h.lower() == 'MIC Upper Limit'.lower():
            elemental_value_column = header_row.index(h)
    # sort list by material codes to allow for faster lookup later
    elemental_info = sorted(elemental_info, key=lambda row: row[material_code_column])

def build_products(family_group_filepath, elemental_filepath):
    """ Generates a list of all products by reading in from a csv file.
        As of now, the family group file should be 'products.csv' and the 
        elemental file should be ''InspectionPlans.csv' """
    try:
        curr_file = family_group_filepath
        product_info = csv_loader.load_csv_info(family_group_filepath)
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
            try:
                product_code = int(row[0])
            except ValueError:
                #occurs if the product code is not a number
                continue
            product_name = row[1]
            family_group = row[2]
            viscosity_range = [row[3], row[4], row[5]] # low, high and type
            density = row[6]
            viscosity_specs_at_40 = [row[7], row[8], row[9]]
            viscosity_specs_at_100 = [row[10], row[11], row[12]]
            sensitivity = row[13]
            p = product.Product(product_code, product_name, family_group, density, viscosity_range, viscosity_specs_at_40, viscosity_specs_at_100, sensitivity)
            product_list.append(p)
        
        curr_file = elemental_filepath
        load_elemental_info(elemental_filepath)
        for p in product_list:
            assign_elemental_values(p)
        return product_list

    except ValueError as e:
        pass

