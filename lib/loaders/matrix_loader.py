import operator
import xlrd
import os
import configparser
from . import csv_loader

def build_matrix(filepath):
    product_dict = {}
    family_group_list = []
    try:
        matrix_info = csv_loader.load_csv_info(filepath)
        if matrix_info == None:
            print('No matrix info.')
            return
        matrix_rows = []
        for row in matrix_info:
            # we don't want the headers or other junk info. 
            # a cleaner solution should be devised later.
            if row[0] == '': 
                continue
            # build the matrix
            curr_row = []
            for i in range(2, len(row)):
                # we start at two to skip the first 2 columns as they are not part of the matrix
                column_value = row[i]
                try :
                    if not column_value == '':
                       curr_row.append(int(column_value))
                except ValueError:
                    # occurs when the column value is not an integer
                    curr_row = []
                    break
            # add this row to the matrix
            if not curr_row == []: 
                matrix_rows.append(curr_row)

            # add the family group name in this row to a list
            # these should always be valid if a break or continue has not been issued above
            family_group_code = row[1].strip(' ')
            if len(family_group_code) < 1 or len(family_group_code) >3:
                pass #sloppy
            else:
                family_group_list.append(family_group_code)

        num_family_groups = len(family_group_list)
        # verify all rows by checking that they have the correct number of elements
        for r in matrix_rows:
            if not len(r) == num_family_groups:
                matrix_rows.remove(r)
        # create a dictionary to map family group codes to their indices. 
        # this is essentially just an enum
        family_group_indices = dict(zip(family_group_list, range(0, len(family_group_list))))
        return (family_group_indices, matrix_rows)
    except ValueError:
        # this will occur if the line is a header, legend or something else not in the compatible matrix form
        pass
