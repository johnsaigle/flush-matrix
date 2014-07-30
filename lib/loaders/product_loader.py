import os
import xlrd
from ..entities import product

def process_cell(cell):
    """Converts the given cell to the appropriate value."""
    if cell.value == 'NA':
        return '' 
    ttype = cell.ctype # get the cell's 'type'
    if ttype == xlrd.XL_CELL_EMPTY or ttype == xlrd.XL_CELL_TEXT or ttype == xlrd.XL_CELL_BLANK:
        return cell.value
    if ttype == xlrd.XL_CELL_NUMBER or ttype == xlrd.XL_CELL_DATE or ttype == xlrd.XL_CELL_BOOLEAN:
        # convert these types to strings
        return int(cell.value)
    if cell.ctype == xlrd.XL_CELL_ERROR:
        # do not process - instead, return the correct error message
        return xlrd.error_text_from_code[cell.value]

def process_row(row_as_array):
    print(row_as_array[0])
    print('\n')
    """Converts a row into the appropriate text."""
    for cell in row_as_array:
        # print(cell.value)
        cell.value = process_cell(cell)
    return row_as_array

def build_products(filepath):
    """Reads data from excel spreadsheets to build data representations of products."""
    """All attributes of product objects are stored as strings so the user is responsible for casting types."""
    product_list = []
    try:
        workbook = xlrd.open_workbook(filepath)
        print("Loading products from spreadsheet...")
        
        worksheet = workbook.sheet_by_name('FlushData')
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1

        # map column names to indices for readability
        CODE_COL = 0
        NAME_COL = 1
        VISC_40_LOW_COL = 2
        VISC_40_HIGH_COL = 3
        VISC_100_LOW_COL = 4
        VISC_100_HIGH_COL = 5
        row_index = 1
        while row_index < num_rows:
            # sanitize row
            curr_row = process_row(worksheet.row(row_index))

            # we can skip the header rows
            row_index += 1 

            # fetch values from the spreadsheet using xlrd library
            code = curr_row[CODE_COL].value
            name = curr_row[NAME_COL].value
            visc_40_low = curr_row[VISC_40_LOW_COL].value
            visc_40_high = curr_row[VISC_40_HIGH_COL].value
            visc_100_low = curr_row[VISC_100_LOW_COL].value
            visc_100_high = curr_row[VISC_100_HIGH_COL].value
            # all elemental values should be formatted as floats
            elemental_values = {
                    'Aluminum' : curr_row[6].value,
                    'Barium' : curr_row[7].value,
                    'Calcium' : curr_row[8].value,
                    'Copper' : curr_row[9].value,
                    'Iron' : curr_row[10].value,
                    'Lead' : curr_row[11].value,
                    'Nickel' : curr_row[12].value,
                    'Nitrogen' : curr_row[13].value,
                    'Molybdenum' : curr_row[14].value,
                    'Silicon' : curr_row[15].value,
                    'Silver' : curr_row[16].value,
                    'Sulphur' : curr_row[17].value,
                    'Titanium' : curr_row[18].value,
                    'Magnesium' : curr_row[19].value,
                    'Phosphorus' : curr_row[20].value,
                    'Zinc' : curr_row[21].value 
                }
            family_group = curr_row[22].value
            demulse = curr_row[23].value
            dyed = curr_row[24].value
            # create a new product object based on these attributes
            p = product.Product(code, name, elemental_values, demulse, dyed, visc_40_low, visc_40_high, visc_100_low,visc_100_high)
            #add the new product to the list of products to return
            product_list.append(p)
        print("Products loaded: " +str(len(product_list)))
        return product_list

    except ValueError as e:
        print("Value error occurred in processing row #"+str(row_index))
        pass
