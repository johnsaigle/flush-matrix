import xlrd
import configparser
from ..entities import equipment

def build_equipment(filepath):
    global config
    config = configparser.ConfigParser()
    config.read('settings.ini')
    equip_list = []
    workbook = xlrd.open_workbook(filepath)
    equipment_worksheet_name = str(config['File Locations']['Title of Equipment Worksheet'])
    worksheet = workbook.sheet_by_name(equipment_worksheet_name)
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = 0 # header row

    print("Loading equipment from spreadsheet at {0}...".format(filepath))

    while curr_row < num_rows:
        curr_row += 1
        # stop at the first blank cell in the first (0th) column
        ttype = worksheet.cell_type(curr_row, 0)
        if ttype == 0:
            break
        name = worksheet.cell_value(curr_row, 0)
        area = worksheet.cell_value(curr_row, 1)
        residual_volume = worksheet.cell_value(curr_row, 2)
        cycle_size = worksheet.cell_value(curr_row, 3)
        initial_fill = worksheet.cell_value(curr_row, 4)
        flush_material = worksheet.cell_value(curr_row, 5)
        e = equipment.Equipment(name, area, residual_volume, cycle_size, flush_material, initial_fill)
        equip_list.append(e)

    print("Pieces of equipment loaded: " + str(len(equip_list)))
    return equip_list
