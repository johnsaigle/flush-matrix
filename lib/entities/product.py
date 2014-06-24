from collections import namedtuple
class Product:
    def __init__(self, material_code, name, elemental_values, viscosity_at_40_low=None, viscosity_at_40_high=None,viscosity_at_100_low =None, viscosity_at_100_high=None):
        self.name = name
        self.material_code = material_code # a numerical product code
        self.elemental_values = elemental_values # dictionary mapping the names of elements to their percentage value
        Viscosity = namedtuple('Viscosity', 'low high')
        self.viscosity_at_40 = Viscosity(viscosity_at_40_low, viscosity_at_40_high)
        self.viscosity_at_100 = Viscosity(viscosity_at_100_low, viscosity_at_100_high)
        self.family_group = '0' # will be pulled from excel later
    
    def calculate_average_viscosity_at_100(self):
        # use 100. If 100 is None or '', use 40. If 40 is None or '', error
        if self.viscosity_at_100.low == None or self.viscosity_at_100.low == '':
            return 0
        elif self.viscosity_at_100.high == None or self.viscosity_at_100.high == '':
            return 0
        else:
            # assuming here that the values are valid
            return (viscosity_at_100.high - viscosity_at_40.high)/2

    def calculate_average_viscosity_at_40(self):
        if self.viscosity_at_40.low == None or self.viscosity_at_40.low == '':
            return 0
        elif self.viscosity_at_40.high == None or self.viscosity_at_40.high == '':
            return 0
        else:
            # assuming here that the values are valid
            return (viscosity_at_40.high - viscosity_at_40.high)/2
