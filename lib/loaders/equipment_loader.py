import xlrd

def build_equipment(filepath):
    equip_list = []
    workbook = xlrd.open_workbook(filepath)
    num_rows = worksheet.nrows - 1
    num_cells = worksheet.ncols - 1
    curr_row = 0 # header row
    while curr_row < num_rows:
        curr_row += 1
        name = worksheet.cell_value(curr_row, 0)
        area = worksheet.cell_value(curr_row, 1)
        residual_volume = worksheet.cell_value(curr_row, 2)
        cycle_size = worksheet.cell_value(curr_row, 3)
        initial_fill = worksheet.cell_value(curr_row, 4)
        flush_material = worksheet.cell_value(curr_row, 5)
        e = equipment.Equipment(name, area, residual_volume, cycle_size, flush_material, initial_fill)
        equip_list.append(e)
    return equip_list
    
