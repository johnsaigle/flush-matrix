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
    message = "Looking for match for product code "+str(product_code)+"."
    print(message)
    product = None
    for p in products:
        if p.material_code == product_code:
            product = p
            print("Match found: "+str(product_code)+".")
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
        sys.exit(1)
    except Exception as e:
        print("An unspecified exception occurred -- " +str(e))

    products = load_products(generate_file_path(product_file_name))
    equipment = load_equipment(generate_file_path(equipment_file_name))
### END Data Validation Functions ####

def ln_partial(viscosity_value, percentage_in_blend):
    """Returns the partial ln of a product given its viscosity and concentration in a blend."""
    try:
        return (percentage_in_blend * math.log(viscosity_value)) / math.log(1000*viscosity_value)
    except ValueError as e:
        print("Encountered a Value Error while calculating the ln partial -- " + str(e))
        raise

def get_num_elemental_flushes(initial_concentrations_dictionary, concentration_thresholds, initial_fill_size, residual_volume):
    """Determines the number of flush cycles to be executed based on the passed concentration of a product, its acceptable threshold value, and the volumes involved in the equipment."""
    # initialize variables
    global config
    EPSILON = float(config['Algebraic Values']['Concentration Epsilon']) # used in elemental difference calculations to prevent diminishing returns on flush cycles
    current_concentrations = initial_concentrations_dictionary # dictionary, passed from elemental factor function

    # check for elements above threshold
    elements_above_threshold = []

    # run values through the loop until the formula returns a value less than the concentration threshold for each element
    print("\nNow beginning flush simulations.")
    flush_count = 0
    while True:
        for element in current_concentrations:
            # check for unacceptable elemental levels
            if current_concentrations[element] > concentration_thresholds[element] and abs(current_concentrations[element] - concentration_thresholds[element]) > EPSILON:
                elements_above_threshold.append(element)
    
        if len(elements_above_threshold) > 0:
            # increment the number of flushes if one element is above threshold
            print("Testing "+str(len(elements_above_threshold)) +" elements.")
            flush_count += 1
            # calculate new concentrations based on a simulated flush
            print("Current elemental concentrations, flush cycle " +str(flush_count))
            for element in elements_above_threshold:
                print(element + " "+str(current_concentrations[element]))
                # use diluation formula to adjust the values for the elementla conccentrations in the blend
                current_concentrations[element] = (residual_volume * current_concentrations[element] + initial_fill_size * concentration_thresholds[element]) / (initial_fill_size + residual_volume)
            print("Resulting concentrations:")
            for element in elements_above_threshold:
                print(element + " "+str(current_concentrations[element]))

            # clear list of elements above threshold so that it can be cleanly populated in the next loop
            elements_above_threshold = []
        else:
            print("All values now within acceptable range ({0}%) of target.".format(100*EPSILON))
            break

    return flush_count

def _generate_elemental_factor(prev_product, next_product, destination, source = None, volume = None):
    """Compares every element a product has in common and 
    determines the number of flushes necessary to bring the difference between 
    these elemental values to an acceptable level."""
    print("\nNow calculating number of cyles needed for elemental factor...")
    if len(prev_product.elemental_values) >= len(next_product.elemental_values):
        smaller_dictionary = next_product.elemental_values
        larger_dictionary = prev_product.elemental_values
    else:
        smaller_dictionary = prev_product.elemental_values
        larger_dictionary = next_product.elemental_values

    print("\nInitial elemental values: ")
    for e in prev_product.elemental_values:
        print(str(e) + " - "+ str(prev_product.elemental_values[e]))

    print("Target elemental values: ")
    for e in next_product.elemental_values:
        print(str(e) + " - "+ str(next_product.elemental_values[e]))

    # find common elements by iterating over the smaller dictionary
    initial_concentration = {}
    concentration_threshold = {}
    for element in smaller_dictionary:
        if element in larger_dictionary:
            try:
                if float(smaller_dictionary[element]) > 0 and float(larger_dictionary[element]) > 0:
                    initial_concentration[element] = float(prev_product.elemental_values[element])
                    concentration_threshold[element] = float(next_product.elemental_values[element])
            except ValueError:
                print("Products contain invalid values for field " +element)
                print("Previous product: "+prev_product.elemental_values[element])
                print("Next product: "+next_product.elemental_values[element])
                continue

    if len(initial_concentration) > 0:
        print("\nProducts have " +str(len(initial_concentration)) +" element(s) in common:")
        for key in initial_concentration:
            print("-"+str(key))
    else:
        print("\nProducts have no elements in common.")
        return 0
    # determine number of flushes 
    if destination.area == 'Packaging':
        initial_volume = destination.initial_fill_size
    else:
        initial_volume = volume

    num_flushes = get_num_elemental_flushes(initial_concentration, concentration_threshold, initial_volume, destination.residual_volume)
    print("Number of cycles needed for elemental factor: " +str(num_flushes))
    return num_flushes

def _generate_viscosity_factor(prev_product, next_product, destination, volume = None):
    """Determines the flush volume necessary to bring about 
    acceptable levels of viscosity for the next product."""
    print("\nNow calculating number of cyles needed for viscosity factor...")
    global config
    VISCOSITY_EPSILON = float(config['Algebraic Values']['Viscosity Epsilon'])
    LINEARIZED_VISCOSITY_CONSTANT = float(config['Algebraic Values']['Viscosity Constant'])
    # compare viscosities -- we use the average value at 100 becuase it's more common
    curr_viscosity_avg = prev_product.calculate_average_viscosity_at_100()
    target_viscosity_avg = next_product.calculate_average_viscosity_at_100()
    
    # use average at 40 degrees if the value at 100 is invalid
    if curr_viscosity_avg <= 0 or target_viscosity_avg <= 0:
        curr_viscosity_avg = prev_product.calculate_average_viscosity_at_40()
        target_viscosity_avg = next_product.calculate_average_viscosity_at_40()

    # if we still have invalid values, check the edge case where a prev product has a valid avg at 100 and the next product has a valid avg at 40
    # in this case, we treat it like a demulse test (using the demulse constant)
    if curr_viscosity_avg == 0 or target_viscosity_avg == 0:
        curr_viscosity_avg_at_100 = prev_product.calculate_average_viscosity_at_100()
        target_viscosity_avg_at_40 = next_product.calculate_average_viscosity_at_40()
        if not curr_viscosity_avg_at_100 == 0 and not target_viscosity_avg_at_40 ==0:
            DEMULSE_CONSTANT = int(config['Algebraic Values']['Demulse Constant'])
            print("Treating viscosity factor as 'demulse' (moving from viscosity at 100 -> 40).")
            print("Demulse constant = " + str(DEMULSE_CONSTANT))
            return(DEMULSE_CONSTANT)

        # return an error if we fall through all other options to this point
        print("No viscosity values available. Returning...")
        return -1
    
    # initialize data for calculations
    num_cycles = 0
    flush_product = next_product # default
    # if the equipment is a part of the blending or receiving departments, we will flush using Base Oil 1
    if destination.area == 'Blending' or destination.area == 'Bulk Receiving':
        flush_product = find_match(int(config['Other']['BaseOil1 Product Code']))
    # if the target viscosity is above 300, we will flush using Base Oil 2
    if target_viscosity_avg >= int(config['Algebraic Values']['Viscosity Threshold']):
        flush_product = find_match(int(config['Other']['BaseOil2 Product Code']))

    # Loop if the current viscosity is not within an acceptable limit of the target viscosity
    if not abs(curr_viscosity_avg - target_viscosity_avg) < VISCOSITY_EPSILON:
        while True:
            print("\nCurrent viscosity average: " +str(curr_viscosity_avg))
            print("Target viscosity average: " +str(target_viscosity_avg))

            num_cycles += 1
            if volume is None:
                total_volume = destination.initial_fill_size + num_cycles * destination.cycle_size
            else:
                total_volume = volume + num_cycles * destination.cycle_size
                   
            retention_ratio = float(destination.cycle_size / total_volume)
            retention_ratio_complement = float(1- retention_ratio)

            # calculate ln partials -- % in blend * ln(viscosity) / ln(1000*viscosity) 
            try:
                retention_partial = ln_partial(curr_viscosity_avg, retention_ratio)
            except Exception:
                print("Failed to calculate retention partial.")
                return -1
            try:
                complement_partial = ln_partial(target_viscosity_avg, retention_ratio_complement)
            except Exception:
                print("Failed to calculate complement ln partial") 
                return -1

            sum_of_partials = retention_partial + complement_partial # useful for readability
            intermediate_product = (sum_of_partials * LINEARIZED_VISCOSITY_CONSTANT) /(1 - sum_of_partials)
            resulting_viscosity = math.exp(intermediate_product)
            print("Viscosity result, round " +str(num_cycles) +": " +str(resulting_viscosity))
            curr_viscosity_avg = resulting_viscosity

            # return if the result is within an acceptable range; otherwise loop
            if abs(curr_viscosity_avg - target_viscosity_avg) < VISCOSITY_EPSILON:
                break

    print("Number of cyles needed for viscosity factor: " + str(num_cycles))
    return num_cycles

def generate_flush_factor(prev_product, next_product, destination, source= None, volume = None):
    global products
    global config
    # determine number of cyles needed to yield appropriate elemental concentrations
    if volume is None:
        elemental_cycles = _generate_elemental_factor(prev_product, next_product, destination)
        viscosity_cycles = _generate_viscosity_factor(prev_product, next_product, destination)
    else:
        elemental_cycles = _generate_elemental_factor(prev_product, next_product, destination, source, volume)
        viscosity_cycles = _generate_viscosity_factor(prev_product, next_product, destination, volume)
        
    # demulse factor
    demulse_cycles = 0
    # Four cases in which the demulse constant is needed:
    # demulse --> emulse
    # emluse --> demulse
    # non-demulse --> emulse
    # non-demulse --> demulse
    if (prev_product.demulse_test == "NA" and not next_product.demulse_test == "NA") or (not prev_product.demulse_test == "NA" and not next_product.demulse_test== "NA"):
       print("\nDemulse factor present. Using demulse constant for number of cycles needed to clear demulse contaminants.")
       demulse_cycles = int(config['Algebraic Values']['Demulse Constant'])
    else:
       print("\nNo demulse factor present.")

    # dye factor
    dye_cycles = 0
    if prev_product.dyed == "YES" and next_product.dyed == "NO":
       dye_cycles = int(config['Algebraic Values']['Dye Constant'])
       print("\nDye factor present. \n Using dye constant {0} for number of cycles needed to clear dye contaminants.".format(dye_cycles))
    else:
       print("\nNo dye factor present.")

    flush_cycles = max(elemental_cycles, viscosity_cycles, demulse_cycles, dye_cycles) 
    print("\nFINAL FLUSH FACTOR = max (viscosity cycles, elemental cycles, demulse cycles, dye cycles) = " +str(flush_cycles))
    return flush_cycles


# launch a script component if the GUI isn't used
if __name__ == "__main__":
    init_data()
    global products
    global family_group_matrix
    selection = -1
    if products == None:
        print("Error loading product information. Exiting.")
        sys.exit(1)
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
