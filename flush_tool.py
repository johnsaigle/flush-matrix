#!/usr/bin/python
import math
import sys
import os
import inspect
import configparser
import logging
import datetime
from flushmatrix.lib.loaders import product_loader
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
    # check if products loaded correctly
    if products is None or len(products) < 1:
        logging.error("No products loaded. Returning...")
        return None

    product = None
    for p in products:
        if p.material_code == product_code:
            product = p
            logging.info("Match found: "+str(product_code)+".")
            return product

    # if no product found
    if product == None:
       msg = "Material code '{0}' does not match any product."
       errormsg = msg.format(product_code)
       logging.error(errormsg)
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

    # Initialize the logger
    loggingdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))) + '\\logs\\'
    if not os.path.exists(loggingdir):
        os.makedirs(loggingdir)
    logging.basicConfig(filename=loggingdir + datetime.date.today().isoformat() +'.log', level=logging.INFO)
    logging.info("Initializing data...")

    # load configuration information
    config = configparser.ConfigParser()
    config.read('settings.ini')
    try:
        product_file_name = str(config['File Locations']['Product File Name'])
        equipment_file_name = str(config['File Locations']['Equipment File Name'])
    except KeyError as e:
        logging.error('Key Error occurred when reading settings file - could not find key "%s"' % str(e), exc_info=True)
        sys.exit(-1)
    except Exception as e:
        logging.error("An unspecified exception occurred -- " +str(e), exc_info=True)

    products = load_products(generate_file_path(product_file_name))
    equipment = load_equipment(generate_file_path(equipment_file_name))
### END Data Validation Functions ####

### Calculation functions ###

def ln_partial(viscosity_value, percentage_in_blend):
    """Returns the partial ln of a product given its viscosity and concentration in a blend."""
    try:
        return (percentage_in_blend * math.log(viscosity_value)) / math.log(1000*viscosity_value)
    except ValueError as e:
        logging.error("Encountered a Value Error while calculating the ln partial -- " + str(e), exc_info=True)
        raise

def get_num_elemental_flushes(initial_concentrations_dictionary, concentration_thresholds, initial_fill_size, residual_volume, flush_volume):
    """Determines the number of flush cycles to be executed based on the passed concentration of a product, its acceptable threshold value, and the volumes involved in the equipment."""
    # initialize variables
    global config
    ELEMENTAL_EPSILON = float(config['Algebraic Values']['Concentration Epsilon']) # used in elemental difference calculations to prevent diminishing returns on flush cycles
    current_concentrations = initial_concentrations_dictionary # dictionary, passed from elemental factor function
    elements_above_threshold = []
    flush_count = 0

    logging.info("INITIAL ELEMENTAL TEST (epsilon = {0}):".format(str(ELEMENTAL_EPSILON)))
    for element in current_concentrations:
        # intial check for unacceptable elemental levels
        delta = (residual_volume * current_concentrations[element]) / (initial_fill_size * concentration_thresholds[element])
        logging.info("{0} 'Delta' concentration = {1}. Delta < Epsilon = {2}".format(element, delta, delta < ELEMENTAL_EPSILON))
        if delta > ELEMENTAL_EPSILON:
            elements_above_threshold.append(element)

    if len(elements_above_threshold) == 0:
        logging.info("Elemental test passed: no flush cycles needed.")
        return 0

    # run values through the loop until the formula returns a value less than the concentration threshold for each element
    while True:
        # increment the number of flushes 
        flush_count += 1
        logging.info("Elemental Flush Round ({0}): Testing "+str(len(elements_above_threshold)) +" elements.".format(flush_count))
        # calculate new concentrations based on a simulated flush
        logging.info("Current elemental concentrations:")
        for element in elements_above_threshold:
            logging.info(element + " "+str(current_concentrations[element]))
            # use diluation formula to adjust the values for the elemental concentrations in the blend
            current_concentrations[element] = ((residual_volume + (flush_count * flush_volume)) * current_concentrations[element]) / (initial_fill_size * concentration_thresholds[element])
        
        logging.info("Resulting concentrations after flush:")
        for element in elements_above_threshold:
            logging.info(element + " "+str(current_concentrations[element]))

        # clear list of elements above threshold so that it can be cleanly populated in the next loop
        elements_above_threshold = []

        for element in current_concentrations:
            # check for unacceptable elemental levels
            delta = (residual_volume * current_concentrations[element]) / (initial_fill_size * concentration_thresholds[element])
            logging.info("{0} 'Delta' concentration = {1}. Delta < Epsilon = ".format(delta > ELEMENTAL_EPSILON))
            if delta > ELEMENTAL_EPSILON:
                elements_above_threshold.append(element)

        # if all elements are clear, we can return. Otherwise we loop. 
        if len(elements_above_threshold) == 0:
            logging.info("All values within acceptable range ({0}%) of target.".format(100*ELEMENTAL_EPSILON))
            return flush_count            


def _generate_elemental_factor(prev_product, next_product, destination, volume = None):
    """Compares every element a product has in common and 
    determines the number of flushes necessary to bring the difference between 
    these elemental values to an acceptable level."""
    if len(prev_product.elemental_values) >= len(next_product.elemental_values):
        smaller_dictionary = next_product.elemental_values
        larger_dictionary = prev_product.elemental_values
    else:
        smaller_dictionary = prev_product.elemental_values
        larger_dictionary = next_product.elemental_values

    logging.info("Initial elemental values: ")
    for e in prev_product.elemental_values:
        logging.info(str(e) + " - "+ str(prev_product.elemental_values[e]))

    logging.info("Target elemental values: ")
    for e in next_product.elemental_values:
        logging.info(str(e) + " - "+ str(next_product.elemental_values[e]))

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
                logging.error("Products contain invalid values for field " +element)
                logging.error("Previous product: "+prev_product.elemental_values[element])
                logging.error("Next product: "+next_product.elemental_values[element])
                continue

    if len(initial_concentration) > 0:
        logging.info("Products have " +str(len(initial_concentration)) +" element(s) in common:")
        for key in initial_concentration:
            logging.info("-"+str(key))
    else:
        logging.info("Products have no elements in common.")
        return 0
    # determine number of flushes 
    if destination.area == 'Packaging':
        initial_volume = destination.initial_fill_size
    else:
        initial_volume = volume

    num_flushes = get_num_elemental_flushes(initial_concentration, concentration_threshold, initial_volume, destination.residual_volume, destination.cycle_size)
    logging.info("Number of cycles needed for elemental factor: " +str(num_flushes))
    return num_flushes

def _generate_viscosity_factor(prev_product, next_product, destination, flush_volume, volume = None):
    """Determines the flush volume necessary to bring about 
    acceptable levels of viscosity for the next product."""
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
            DEMULSE_CONSTANT = int(config['Algebraic Values']['Demulse Cycle Count'])
            logging.warning("Treating viscosity factor as 'demulse' (moving from viscosity at 100 -> 40).")
            logging.info("Demulse cycle count = " + str(DEMULSE_CONSTANT))
            return(DEMULSE_CONSTANT)

        # return an error if we fall through all other options to this point
        logging.warning("No viscosity values available. Returning...")
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

    if flush_product == None:
        logging.error("Could not find a match for the flush product. Returning...")
        return -1

    # Loop if the current viscosity is not within an acceptable limit of the target viscosity
    if abs(curr_viscosity_avg - target_viscosity_avg) > (VISCOSITY_EPSILON * target_viscosity_avg):
        while True:
            logging.info("Current viscosity average: " +str(curr_viscosity_avg))
            logging.info("Target viscosity average: " +str(target_viscosity_avg))

            num_cycles += 1
            if volume is None:
                total_volume = destination.initial_fill_size + destination.residual_volume
            else:
                total_volume = volume + destination.residual_volume
                   
            retention_ratio = float(destination.residual_volume / total_volume)
            retention_ratio_complement = float(1 - retention_ratio)

            # calculate ln partials -- % in blend * ln(viscosity) / ln(1000*viscosity) 
            try:
                retention_partial = ln_partial(curr_viscosity_avg, retention_ratio)
            except Exception:
                logging.error("Failed to calculate retention partial.", exc_info=True)
                return -1
            try:
                complement_partial = ln_partial(target_viscosity_avg, retention_ratio_complement)
            except Exception:
                logging.error("Failed to calculate complement ln partial", exc_info=True) 
                return -1

            sum_of_partials = retention_partial + complement_partial # useful for readability
            intermediate_product = (sum_of_partials * LINEARIZED_VISCOSITY_CONSTANT) /(1 - sum_of_partials)
            resulting_viscosity = math.exp(intermediate_product)
            logging.info("Viscosity result, round " +str(num_cycles) +": " +str(resulting_viscosity))
            curr_viscosity_avg = resulting_viscosity

            # return if the result is within an acceptable range; otherwise loop
            if abs(curr_viscosity_avg - target_viscosity_avg) < VISCOSITY_EPSILON:
                break
    else:
        logging.info("Current viscosity average: " +str(curr_viscosity_avg))
        logging.info("Target viscosity average: " +str(target_viscosity_avg))

    logging.info("Number of cyles needed for viscosity factor: " + str(num_cycles))
    return num_cycles

def generate_flush_factor(prev_product, next_product, destination, volume = None):
    global products
    global config
    """ Determine number of cyles needed to yield appropriate elemental concentrations. """

    # for packaging operation, where a volume need not be specified
    if volume is None:
        elemental_cycles = _generate_elemental_factor(prev_product, next_product, destination)
        viscosity_cycles = _generate_viscosity_factor(prev_product, next_product, destination)
    else:
        elemental_cycles = _generate_elemental_factor(prev_product, next_product, destination, volume)
        viscosity_cycles = _generate_viscosity_factor(prev_product, next_product, destination, volume)
        
    # demulse factor
    demulse_cycles = 0
    # Four cases in which the demulse constant is needed:
    # demulse --> emulse
    # emluse --> demulse
    # non-demulse --> emulse
    # non-demulse --> demulse
    if (prev_product.demulse_test == "" and not next_product.demulse_test == "") or (not prev_product.demulse_test == "" and not next_product.demulse_test== ""):
       logging.info("Demulse factor present. Using demulse cycle count for number of cycles needed to clear demulse contaminants.")
       demulse_cycles = int(config['Algebraic Values']['Demulse Cycle Count'])
    else:
       logging.info("No demulse factor present.")

    # dye factor
    dye_cycles = 0
    if prev_product.dyed == "YES" and next_product.dyed == "NO":
       dye_cycles = int(config['Algebraic Values']['Dye Cycle Count'])
       logging.info("Dye factor present. Using dye cycle count {0} for number of cycles needed to clear dye contaminants.".format(dye_cycles))
    else:
       logging.info("No dye factor present.")

    flush_cycles = max(elemental_cycles, viscosity_cycles, demulse_cycles, dye_cycles) 
    logging.info("FINAL FLUSH FACTOR moving from " +str(prev_product.material_code) + " to " +str(next_product.material_code) +" = max (viscosity cycles, elemental cycles, demulse cycles, dye cycles) = " +str(flush_cycles))
    return flush_cycles


# launch a script component if the GUI isn't used
if __name__ == "__main__":
    """Script component if launched from command line. Note: Severely deprecated since gui component added."""
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
