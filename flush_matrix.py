#!/usr/bin/python
import math
import sys
import os
import inspect
from flushmatrix.lib.loaders import product_loader
from flushmatrix.lib.loaders import matrix_loader
from flushmatrix.lib.entities import product

class MyException(Exception):
    pass

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

def _generate_family_group_factor(prev_family_group, next_family_group):
    prev_index = family_group_indices[prev_family_group]
    next_index = family_group_indices[next_family_group]
    print ("Prev: {0}. Index = {1}".format(prev_family_group, prev_index))
    print ("Next: {0}. Index = {1}".format(next_family_group, next_index))
    family_group_factor = family_group_matrix[prev_index][next_index]

    family_group_factor += 1

    print("Family group factor: "+str(family_group_factor))
    return family_group_factor

def _generate_elemental_factor(prev_product, next_product):
    if len(prev_product.elemental_values) > len(next_product.elemental_values):
        smaller_dictionary = next_product.elemental_values
        larger_dictionary = prev_product.elemental_values
    else:
        smaller_dictionary = prev_product.elemental_values
        larger_dictionary = next_product.elemental_values

    # find common elements by iterating over the smaller list
    shared_elements = []
    for element in smaller_dictionary:
        if element in larger_dictionary:
            shared_elements.append(element)

    # return 1 if there are no shared elements
    if shared_elements == []:
        print("No shared elements.")
        return 1
    # find the greatest difference between shared elements
    elemental_differences = []
    for element in shared_elements:
        prev_value = float(prev_product.elemental_values[element])
        next_value = float(next_product.elemental_values[element])
        max_value = max([prev_value, next_value])
        min_value = min([prev_value, next_value])
        elemental_differences.append((max_value - min_value)/min_value)
    elemental_factor = int(max(elemental_differences))

    if elemental_factor == 0:
        # all elemental values are the same. we will use a multiplier of 1
        elemental_factor = 1

    print("Elemental factor: " + str(elemental_factor))
    return elemental_factor

def _generate_viscosity_factor(prev_product, next_product):
    # compare viscosities -- we use the average value at 100 becuase it's more common
    typical_viscosity_index = 2 # according to Product data structure
    prev_viscosity_avg = prev_product.viscosity_specs_at_100[typical_viscosity_index] # this variable is a tuple; the '2th' value is 'Typ' -- the typical (or average) cSt measurement for the product
    next_viscosity_avg = next_product.viscosity_specs_at_100[typical_viscosity_index] 
    # if there is no proepr value for either average, use specs at 40 instead
    if prev_viscosity_avg == None or prev_viscosity_avg == '' or next_viscosity_avg == None or next_viscosity_avg == '':
        prev_viscosity_avg = prev_product.viscosity_specs_at_40[typical_viscosity_index] 
        next_viscosity_avg = next_product.viscosity_specs_at_40[typical_viscosity_index] 
    difference = abs(float(prev_viscosity_avg) - float(next_viscosity_avg)) # absolute difference between values
    # normalize the difference based on some value decided by the user
    normalization_interval = 3.0 # magic number until I create the config file
    adjusted_difference_factor = 0.1 * int(difference / normalization_interval) # cast to integer here because theremainder is not important to us
    viscosity_factor = 1.0 + adjusted_difference_factor # 1.0 is the default factor 
    print("Viscosity factor: "+str(viscosity_factor))
    return viscosity_factor

def generate_flush_factor(prev_one, next_one):
    global products
    if products is None:
        init_data()
    
    # a bit of a duct tape fix between ui and text-based modes... should refactor later
    if type(prev_one) is int:
        prev_product = find_match(prev_one)
    else:
        prev_product = prev_one
    if type(next_one) is int:
        next_product = find_match(next_one)
    else:
        next_product = next_one

    family_group_factor = 1
    viscosity_factor = 1
    elemental_factor = 1
    equipment_factor = 1 # may not need this in the end
    # determine family group factor
    prev_family_group = prev_product.family_group.lower() 
    next_family_group = next_product.family_group.lower()
    family_group_factor = _generate_family_group_factor(prev_family_group, next_family_group)
    #determine elemental factor if products share a family group
    elemental_factor = _generate_elemental_factor(prev_product, next_product)
    # viscosity factor -- use averages and determine the difference
    viscosity_factor = _generate_viscosity_factor(prev_product, next_product)
    # demulse factor
    if prev_product.demulse_test == True or next_product.demulse_test == False:
        print("Demulse factor present.")
    core_factor = family_group_factor + viscosity_factor
    if core_factor < 3:
        print("Sum of family group factor and viscosity factor is less than 3. Core factor set to 0.")
        core_factor = 0
    flush_factor = core_factor * elemental_factor 
    return flush_factor

def load_products(product_filepath, elemental_filepath):
    return (product_loader.build_products(product_filepath, elemental_filepath))

def load_matrix(filepath):
    return (matrix_loader.build_matrix(filepath))

def find_match(product_code):
    global products
    product = None
    for p in products:
        if p.material_code == product_code:
            product = p
            return product

    # if no product found
    if product == None:
       msg = "Material code '{0}' does not match any product."
       errormsg = msg.format(product_code)
       print(errormsg)
       return None

def find_data_file(filename):
    if getattr(sys, 'frozen', False):
    # THe application is frozen (cx_freeze)
        datadir = os.path.dirname(sys.executable)
    else:
        # not frozen
        datadir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '\\data\\'
    return os.path.join(datadir, filename)

def init_data():
    global products
    global family_group_indices
    global family_group_matrix
    products = load_products(find_data_file('products.csv'), find_data_file('InspectionPlans.csv'))
    matrix_info = load_matrix(find_data_file('matrix.csv'))
    family_group_indices = matrix_info[0]
    family_group_matrix = matrix_info[1]

#MAIN
#working_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) # this will return the filepath of the src directory
#print(working_dir)
#if working_dir.endswith('/src'): # unix 
#    script_root_directory = working_dir[:-4] # removes the final four characters
#    data_directory = script_root_directory + '/data/'
#elif working_dir.endswith('\\src'): #windows
#    script_root_directory = working_dir[:-4] # removes the final four characters
#    data_directory = script_root_directory + '\\data\\'
#else:
#    print ("Loading error: script not launched from within src directory")
#    sys.exit()
if __name__ == "__main__":
    init_data()
    global products
    global family_group_matrix
    selection = -1
    # allow user to enter in product information
    for i, p in zip(range(len(products)), products):
        print(str(i) + " -- " + str(p.material_code))
    while True:
        try:
            prev_product = None
            selection = input("Enter product code for previous product: ")
            selection = int(selection)
            prev_product = find_match(selection)
            if not prev_product is None:
                break
    
        except (ValueError, KeyError) as e:
            if e is ValueError:
                print("Selection must be a number.")
            if e is KeyError:
                print("Code does not correspond to any product.")
            continue
    while True:
        try:
            next_product = None
            selection = input("Enter product code for next product: ")
            selection = int(selection)
            next_product = find_match(selection)
            if not next_product is None:
                break
    
        except (ValueError, KeyError) as e:
            if e is ValueError:
                print("Selection must be a number.")
            if e is KeyError:
                print("Code does not correspond to any product.")
            continue
    print(prev_product.name, next_product.name)
    flush_factor = generate_flush_factor(prev_product, next_product)
    print("Overall flush factor: "+str(flush_factor))

