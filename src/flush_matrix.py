#!/usr/bin/python
import sys
import os
import inspect
from flushmatrix.lib.loaders import product_loader
from flushmatrix.lib.loaders import matrix_loader
from flushmatrix.lib.entities import product

try: 
    pass
    #from lib.loaders import product_loader
    #from lib.entities import product
except ImportError:
    working_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # this will return the filepath of the src directory
    if working_dir in sys.path: 
        raise
    sys.path.append(working_dir)
    from lib.loaders import product_loader
    from lib.entities import product

def generate_flush_factor(next_product, prev_product):
    global products
    family_group_factor = 0
    viscosity_factor = 0
    elemental_factor = 0
    equipment_factor = 0
    # determine family group factor

    core_factor = family_group_factor + viscosity_factor
    if core_factor < 3:
        core_factor = 0
    flush_factor = core_factor * elemental_factor * equipment_factor
    return flush_factor
def load_products(filepath):
    return (product_loader.build_products(filepath))

def load_matrix(filepath):
    return (matrix_loader.build_matrix(filepath))

def init_data(data_directory):
    global products
    global family_group_indices
    global family_group_matrix
    products = load_products(data_directory + 'products.csv')
    matrix_info = load_matrix(data_directory + 'matrix.csv')
    family_group_indices = matrix_info[0]
    family_group_matrix = matrix_info[1]

#MAIN
working_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # this will return the filepath of the src directory
print(working_dir)
if working_dir.endswith('/src'): # unix 
    script_root_directory = working_dir[:-4] # removes the final four characters
    data_directory = script_root_directory + '/data/'
elif working_dir.endswith('\\src'): #windows
    script_root_directory = working_dir[:-4] # removes the final four characters
    data_directory = script_root_directory + '\\data\\'
else:
    print ("Loading error: script not launched from within src directory")
    sys.exit()
init_data(data_directory)
global products
global family_group_matrix
print(products)
print(family_group_matrix)
selection = -1
# allow user to enter in product information
for i, p in zip(range(len(products)), products):
    print(str(i) + " -- " + p.name)
while True:
    try:
        selection = input("Enter number for previous product: ")
        if len(selection) < 1 or len(selection) > 2:
            print("Invalid input size: should be one or two characters.")
            continue
        selection = int(selection)
        if selection < 0 or selection > len(products):
            print("Selection is out of range.")
            continue
        else:
            prev_product = products[selection]
            break

    except (ValueError, KeyError) as e:
        if e is ValueError:
            print("Selection must be a number.")
        if e is KeyError:
            print("Code does not correspond to any product.")
        continue
while True:
    try:
        selection = input("Enter number for next product: ")
        if len(selection) < 1 or len(selection) > 2:
            print("Invalid input size: should be one or two characters.")
            continue
        selection = int(selection)
        if selection < 0 or selection > len(products):
            print("Selection is out of range.")
            continue
        else:
            next_product = products[selection]
            break

    except (ValueError, KeyError) as e:
        if e is ValueError:
            print("Selection must be a number.")
        if e is KeyError:
            print("Code does not correspond to any product.")
        continue
generate_flush_factor(prev_product, next_product)
