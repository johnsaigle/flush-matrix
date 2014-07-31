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


### LOADING FUNCTIONS ###
def load_products(product_filepath):
    """Make a call to product loader to load product information from an excel file."""
    return (product_loader.build_products(product_filepath))

def load_matrix(filepath):
    """Make a call to matrix_loader to load family goup matrix information from a csv file"""
    return (matrix_loader.build_matrix(filepath))
def load_equipment(filepath):
    """Make a call to equipment_loader to load equipment information from an excel file into memory."""
    return (equipment_loader.build_equipment(filepath))
### END LOADING FUCNTIONS ###

### Data Validation Functions ### 
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

def generate_file_path(filename):
    """Returns a valid filepath, if file 'filename' exists."""
    if getattr(sys, 'frozen', False):
    # The application is frozen (cx_freeze)
        datadir = os.path.dirname(sys.executable)
    else:
        # not frozen
        datadir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '\\data\\'
    return os.path.join(datadir, filename)

def init_data():
    """Load all external values into the program memory."""
    """These values can be customized in the file 'settings.ini '"""
    global config
    global products
    global equipment

    print("Initializing data...")

    # load configuration information
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        product_file_name = str(config['File Locations']['Product File Name'])
        equipment_file_name = str(config['File Locations']['Equipment File Name'])
    except KeyError as e:
        print('Key Error occurred when reading settings file - could not find key "%s"' % str(e))
        quit()
    except Exception as e:
        print("An unspecified exception occurred -- " +str(e))

    products = load_products(generate_file_path(product_file_name))
    equipment = load_equipment(generate_file_path(equipment_file_name))
### END Data Validation Functions ####

def ln_partial(viscosity_value, percentage_in_blend):
    """Returns the partial ln of a product given its viscosity and concentration in a blend."""
    return (percentage_in_blend * math.log(viscosity_value)) / math.log(1000*viscosity_value)

def get_num_elemental_flushes(initial_concentrations_dictionary, concentration_thresholds, initial_fill_size, residual_volume):
    """Determines the number of flush cycles to be executed based on the passed concentration of a product, its acceptable threshold value, and the volumes involved in the equipment."""
    # initialize variables
    global config
    EPSILON = float(config['Algebraic Values']['Concentration Epsilon']) # used in elemental difference calculations to prevent diminishing returns on flush cycles
    current_concentrations = initial_concentrations_dictionary # dictionary, passed from elemental factor function

    # check for elements above threshold
    flush_count = 0
    elements_above_threshold = []

    # run values through the loop until the formula returns a value less than the concentration threshold for each element
    while True:
        num_elements_to_test = 0
        for element in current_concentrations:
            # check for unacceptable elemental levels
            if current_concentrations[element] > concentration_thresholds[element] and abs(current_concentrations[element] - concentration_thresholds[element]) > EPSILON:
                elements_above_threshold.append(element)
    
        if len(elements_above_threshold) > 0:
            # increment the number of flushes if one element is above threshold
            print("Testing "+int(num_elements_to_test) +" elements.")
            flush_count += 1
            # calculate new concentrations based on a simulated flush
            for element in elements_above_threshold:
                print(element + " "+str(concentrations[element]))
                # use diluation formula to adjust the values for the elementla conccentrations in the blend
                current_concentrations[element] = (residual_volume * current_concentrations[element] + blend_volume * concentration_thresholds[element]) / (blend_volume + residual_volume)

            # clear list of elements above threshold so that it can be cleanly populated in the next loop
            elements_above_threshold = []
        else:
            break

    return flush_count

def _generate_elemental_factor(prev_product, next_product, destination, source = None):
    """Compares every element a product has in common and 
    determines the number of flushes necessary to bring the difference between 
    these elemental values to an acceptable level."""
    if len(prev_product.elemental_values) > len(next_product.elemental_values):
        smaller_dictionary = next_product.elemental_values
        larger_dictionary = prev_product.elemental_values
    else:
        smaller_dictionary = prev_product.elemental_values
        larger_dictionary = next_product.elemental_values

    # find common elements by iterating over the smaller dictionary
    initial_concentration = {}
    concentration_threshold = {}
    for element in smaller_dictionary:
        if element in larger_dictionary:
            try:
                if int(smaller_dictionary[element]) > 0 and int(larger_dictionary[element]) > 0:
                    initial_concentration[element] = int(prev_product.elemental_values[element])
                    concentration_threshold[element] = int(next_product.elemental_values[element])
            except ValueError:
                print("Products contain invalid values for field " +element)
                print("Previous product: "+prev_product.elemental_values[element])
                print("Next product: "+next_product.elemental_values[element])
                continue

    if len(initial_concentration) > 0:
        print("Products have " +str(len(initial_concentration)) +" elements in common:")
        for key in initial_concentration:
            print(str(key))
    else:
        print("Products have no elements in common.")
        return 0
    # determine number of flushes 
    if destination.area == 'Packaging':
        volume = destination.initial_fill_size
    num_flushes = get_num_elemental_flushes(initial_concentration, concentration_threshold, volume, destination.residual_volume)
    print("Number of flushes needed to satisfy elemental factor: " +int(num_flushes))
    return num_flushes

def _generate_viscosity_factor(prev_product, next_product):
    """Determines the flush volume necessary to bring about 
    acceptable levels of viscosity for the next product."""
    global config
    LINEARIZED_VISCOSITY_CONSTANT = float(config['Algebraic Values']['Viscosity Constant'])
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

    sum_of_partials = prev_partial + next_partial # useful for readability
    intermediate_product = (sum_of_partials * LINEARIZED_VISCOSITY_CONSTANT) /(1 - sum_of_partials)
    final_viscosity = math.exp(intermediate_product)

    print("Final viscosity = "+str(final_viscosity))
    return final_viscosity

def generate_flush_factor(prev_product, next_product, destination, source= None):
    global products
    global config
    # determine number of cyles needed to yield appropriate elemental concentrations
    elemental_cycles = _generate_elemental_factor(prev_product, next_product, destination)
    # viscosity factor -- use averages and determine the difference
    viscosity_cycles = _generate_viscosity_factor(prev_product, next_product)

    # demulse factor
    demulse_cycles = 0
    # Four cases in which the demulse constant is needed:
    # demulse --> emulse
    # emluse --> demulse
    # non-demulse --> emulse
    # non-demulse --> demulse
    if (prev_product.demulse_test == "NA" and not next_product.demulse_test == "NA") or (not prev_product.demulse_test == "NA" and not next_product.demulse_test== "NA"):
       print("Demulse factor present. Using demulse constant for number of cycles needed to clear demulse contaminants.")
       demulse_cycles = int(config['Algebraic Values']['Demulse Constant'])
    else:
       print("No demulse factor present.")

    # dye factor
    dye_cycles = 0
    if prev_product.dyed == "YES" and next_product.dyed == "NO":
       print("Dye factor present. Using dye constant for number of cycles needed to clear dye contaminants.")
       dye_cycles = int(config['Algebraic Values']['Dye Constant'])
    else:
       print("No dye factor present.")

    flush_cycles = max(elemental_cycles, viscosity_cycles, demulse_cycles, dye_cycles) 
    print("Final flush factor = max (viscosity cycles, elemental cycles, demulse_cycles, dye cycles) = " +str(flush_cycles))
    return flush_cycles


# launch a script component if the GUI isn't used
if __name__ == "__main__":
    init_data()
    global products
    global family_group_matrix
    selection = -1
    if products == None:
        print("Error loading product information. Exiting.")
        quit()
    # print a list of products
    #for p in products:
    #    print(str(p.material_code) + " -- " + str(p.name))
    while True:
    # allow user to enter in product information
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
    # flush_factor = generate_flush_factor(prev_product, next_product)
    print("Overall flush factor: "+str(flush_factor))
