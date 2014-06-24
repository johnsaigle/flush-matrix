import os
import xlrd
from . import csv_loader
from ..entities import product

#def process_row(row):
    #for cell in row:
        #if cell.value ==

def build_products(filepath):
    """Reads data from excel spreadsheets to build data representations of products"""
    product_list = []
    try:
        workbook = xlrd.open_workbook(filepath)
        print("Loading products from excel...")
        # build products
        worksheet = workbook.sheet_by_name('Product Information')
        num_rows = worksheet.nrows - 1
        num_cells = worksheet.ncols - 1

        # map column names to indices for readability
        CODE_COL = 0
        NAME_COL = 1
        VISC_40_LOW_COL = 2
        VISC_40_HIGH_COL = 3
        VISC_100_LOW_COL = 4
        VISC_100_HIGH_COL = 5
        curr_row = 1
        while curr_row < num_rows:
            # eliminate N/A values
#            process_row(row)
            curr_row += 1 # we can skip the header rows
            code = int(worksheet.cell_value(curr_row, CODE_COL))
            name = worksheet.cell_value(curr_row, NAME_COL)
            visc_40_low = worksheet.cell_value(curr_row, VISC_40_LOW_COL)
            visc_40_high = worksheet.cell_value(curr_row, VISC_40_HIGH_COL)
            visc_100_low = worksheet.cell_value(curr_row, VISC_100_LOW_COL)
            visc_100_high = worksheet.cell_value(curr_row, VISC_100_HIGH_COL)
            elemental_values = {
                    'Aluminum' : worksheet.cell_value(curr_row, 6),
                    'Barium' : worksheet.cell_value(curr_row, 7),
                    'Calcium' : worksheet.cell_value(curr_row, 8),
                    'Copper' : worksheet.cell_value(curr_row, 9),
                    'Chromium' : worksheet.cell_value(curr_row, 10),
                    'Iron' : worksheet.cell_value(curr_row, 11),
                    'Lead' : worksheet.cell_value(curr_row, 12),
                    'Nickel' : worksheet.cell_value(curr_row, 13),
                    'Nitrogen' : worksheet.cell_value(curr_row, 14),
                    'Molybdenum' : worksheet.cell_value(curr_row, 15),
                    'Silicon' : worksheet.cell_value(curr_row, 16),
                    'Silver' : worksheet.cell_value(curr_row, 17),
                    'Sulphur' : worksheet.cell_value(curr_row, 18),
                    'Tin' : worksheet.cell_value(curr_row, 19),
                    'Titanium' : worksheet.cell_value(curr_row, 20),
                    'Magnesium' : worksheet.cell_value(curr_row, 21),
                    'Phosphorus' : worksheet.cell_value(curr_row, 22),
                    'Zinc' : worksheet.cell_value(curr_row, 23)
                }
            p = product.Product(code, name, elemental_values, visc_40_low, visc_40_high, visc_100_low,visc_100_high)
            product_list.append(p)
        return product_list

    except ValueError as e:
        pass
