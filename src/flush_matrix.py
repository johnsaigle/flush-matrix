#!/usr/bin/python
import sys
import os
import inspect
from flushmatrix.lib.loaders import product_loader
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

def load_products(filepath):
    return (product_loader.build_products(filepath))

def init_data(data_directory):
    products = load_products(data_directory + 'products.csv')

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
