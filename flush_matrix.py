#!/usr/bin/python
import math
import sys
import os
import inspect
import configparser
from flushmatrix.lib.loaders import product_loader
from flushmatrix.lib.loaders import matrix_loader
from flushmatrix.lib.loaders import equipment_loader
from flushmatrix.lib.entities import product
from flushmatrix.lib.entities import equipment

# load configuration settings
global config
config = configparser.ConfigParser()
config.read('settings.ini')

def ln_partial(viscosity_value, percentage_in_blend):
    """Returns the partial ln of a product given its viscosity and concentration in a blend."""
    return (percentage_in_blend * math.log(viscosity_value)) / math.log(1000*viscosity_value)

def get_num_flushes(previous_concentration, concentration_thresholds, blend_volume, holdup_volume):
    """Determines the number of flush cycles to be executed based on the passed concentration of a product, its acceptable threshold value, and the volumes involved in the equipment."""
    global config
    EPSILON = float(config['DEFAULT']['Concentration Epsilon']) # used in elemental difference calculations to prevent diminishing returns on flush cycles
    concentrations = previous_concentration # dictionary, passed from elemental factor function
    # check for elements above threshold
    flush_count = 0
    elements_above_threshold = []
    while True:
        num_elements_to_test = 0
        for element in concentrations:
            # increment the number of flushes if one element is above threshold
            if concentrations[element] > concentration_thresholds[element] and abs(concentrations[element] - concentration_thresholds[element]) > EPSILON:
                elements_above_threshold.append(element)
                num_elements_to_test += 1
    
        if num_elements_to_test > 0:
            flush_count += 1
            # calculate new concentrations based on a simulated flush
            for element in elements_above_threshold:
                print(element + " "+str(concentrations[element]))
                concentrations[element] = (holdup_volume * concentrations[element] + blend_volume * concentration_thresholds[element]) / (blend_volume + holdup_volume)
            elements_above_threshold = []
        else:
            break

    return flush_count

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
    """Compares every element a product has in common and 
    determines the number of flushes necessary to bring the difference between 
    these elemental values to an acceptable level."""
    if len(prev_product.elemental_values) > len(next_product.elemental_values):
        smaller_dictionary = next_product.elemental_values
        larger_dictionary = prev_product.elemental_values
    else:
        smaller_dictionary = prev_product.elemental_values
        larger_dictionary = next_product.elemental_values

    # find common elements by iterating over the smaller list
    initial_concentration = {}
    concentration_threshold = {}
    for element in smaller_dictionary:
        if element in larger_dictionary:
            # make sure there are no errors
            try:
                if int(smaller_dictionary[element]) > 0 and int(larger_dictionary[element]) > 0:
                    initial_concentration[element] = int(prev_product.elemental_values[element])
                    concentration_threshold[element] = int(next_product.elemental_values[element])
            except ValueError:
                print("Products contain invalid values for field " +element)
                print("Previous product: "+prev_product.elemental_values[element])
                print("Next product: "+next_product.elemental_values[element])
                continue

    # determine number of flushes 
    flushes = get_num_flushes(initial_concentration, concentration_threshold, 200, 40)
    print("Num flushes: "+str(flushes))
    return flushes

def _generate_viscosity_factor(prev_product, next_product):
    """Determines the flush volume necessary to bring about 
    acceptable levels of viscosity for the next product."""
    global config
    LINEARIZED_VISCOSITY_CONSTANT = float(config['DEFAULT']['Viscosity Constant'])
    # compare viscosities -- we use the average value at 100 becuase it's more common

    prev_viscosity_avg = prev_product.calculate_average_viscosity_at_100()
    next_viscosity_avg = next_product.calculate_average_viscosity_at_100()
    
    # use average at 40 degrees if the value at 100 is invalid
    if prev_viscosity_avg == 0 or next_viscosity_avg == 0:
        prev_viscosity_avg = prev_product.calculate_average_viscosity_at_40()
        next_viscosity_avg = next_product.calculate_average_viscosity_at_40()

    #if prev_percent_in_blend + next_percent_in_blend > 1.0:
    #    print("Error: the sum of viscosity 'percentage in blend' values are greater than 100%.")
    #    return # return a proper value later, or error check in calling function
    
####DUMMY VALUES#####
    prev_percent_in_blend = 10
    next_percent_in_blend = 10
#####

    # calculate ln partials -- avg * ln(% in blend) / ln(1000*% in blend) 
    prev_partial = ln_partial(prev_viscosity_avg, prev_percent_in_blend)

    next_partial = ln_partial(next_viscosity_avg, next_percent_in_blend)

    partial_sum = prev_partial + next_partial
    intermediate_product = (partial_sum * LINEARIZED_VISCOSITY_CONSTANT) /(1 - partial_sum)
    final_viscosity = math.exp(intermediate_product)

    print("Final viscosity = "+str(final_viscosity))
    return final_viscosity

def generate_flush_factor(prev_product, next_product):
    global products

    # initialize products from their material code

    family_group_factor = 1
    viscosity_factor = 1
    elemental_factor = 1
    equipment_factor = 1 # may not need this in the end

    # determine family group factor
    #prev_family_group = prev_product.family_group.lower() 
    #next_family_group = next_product.family_group.lower()
    #family_group_factor = _generate_family_group_factor(prev_family_group, next_family_group)
    # determine number of cyles needed to yield appropriate elemental concentrations
    elemental_factor = _generate_elemental_factor(prev_product, next_product)
    # viscosity factor -- use averages and determine the difference
    viscosity_factor = _generate_viscosity_factor(prev_product, next_product)

    # demulse factor
    if prev_product.demulse == "DM" or next_product.demulse_test == "DM":
       print("Demulse factor present.")
    else:
       print("No demulse factor present.")

    # dye factor
    if prev_product.dyed == "YES" or next_product.dyed == "YES":
       print("Dye factor present.")
    else:
       print("No dye factor present.")

    flush_factor = max(viscosity_factor, elemental_factor) 
    print("Final flush factor = max (viscosity factor, elemental factor) = " +str(flush_factor))
    return flush_factor

def load_products(product_filepath):
    return (product_loader.build_products(product_filepath))

def load_matrix(filepath):
    return (matrix_loader.build_matrix(filepath))

def find_match(product_code):
    global products
    if products is None or len(products) < 1:
        print("No products loaded. Returning...")
        return None
    message = "Looking for match for product code "+str(product_code)
    print(message)
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
    global config
    global family_group_indices
    global family_group_matrix
    print("Initializing data...")
    product_file_name = str(config['DEFAULT']['Product File Name'])
    family_group_matrix_file_name = str(config['DEFAULT']['Family Matrix File Name'])
    products = load_products(find_data_file(product_file_name))
    matrix_info = load_matrix(find_data_file(family_group_matrix_file_name)) #change this to excel later, not csv file anymore
    family_group_indices = matrix_info[0]
    family_group_matrix = matrix_info[1]

# launch a script component if the GUI isn't used
if __name__ == "__main__":
    init_data()
    global products
    global family_group_matrix
    selection = -1
    if products == None:
        print("Error loading product information. Exiting.")
        quit()
    # allow user to enter in product information
    for p in products:
        print(str(p.material_code) + " -- " + str(p.name))
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
