import os
import xlrd
from . import csv_loader
from ..entities import product

global list_of_elements
list_of_elements = [ 'Barium', # this should later be initialized in a config file
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
                element_dictionary[e] = curr_row[elemental_value_column]
        #check for demulsification
        demulse_text = 'Demulsibility @ 54C Emulsion'.lower()
        if product.demulse_test == False and demulse_text in curr_row[elemental_value_column]:
            product.demulse_test = True
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
            print("Upper limit index:" +str(elemental_value_column))
    # sort list by material codes to allow for faster lookup later
    elemental_info = sorted(elemental_info, key=lambda row: row[material_code_column])

def build_products(filepath):
    """ Generates a list of all products by reading in from a csv file.
        As of now, the family group file should be 'products.csv' and the 
        elemental file should be ''InspectionPlans.csv' """
    try:
        product_book = xlrd.open_workbook(filepath)
        print("The number of worksheets is " + str(product_book.sheets))
        print("Sheet names: ")
        print(product_book.sheet_names())
        product_sheet = product_book.sheet_by_name('Products')
        for index in range(product_sheet.nrows):
            print (product_sheet.row(index))
        product_list = None
        return product_list

    except ValueError as e:
        pass

