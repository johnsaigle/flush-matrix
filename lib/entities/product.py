from collections import namedtuple
class Product:
    def __init__(self, material_code, name, elemental_values, demulse, dyed, viscosity_at_40_low=None, viscosity_at_40_high=None,viscosity_at_100_low =None, viscosity_at_100_high=None):
        self.name = name
        self.material_code = material_code # a numerical product code
        self.elemental_values = elemental_values # dictionary mapping the names of elements to their percentage value
        Viscosity = namedtuple('Viscosity', 'low high')
        self.viscosity_at_40 = Viscosity(viscosity_at_40_low, viscosity_at_40_high)
        self.viscosity_at_100 = Viscosity(viscosity_at_100_low, viscosity_at_100_high)
        self.demulse = demulse 
        self.dyed = dyed 
        self.family_group = '0' # will be pulled from excel later

        # sanitize elemental dictionary to remove bogus values (such as 'NA')
        to_del = []                 
        for e in self.elemental_values:
            if elemental_values[e] == 'NA' or elemental_values[e] == None or elemental_values[e] == '':
                to_del.append(e)        # mark to be deleted
        for e in to_del:                # because we can't delete elements 
            del elemental_values[e]     # as they are being iterated
    
    def calculate_average_viscosity_at_100(self):
        # use 100. If 100 is None or '', use 40. If 40 is None or '', error
        if self.viscosity_at_100.low == None or self.viscosity_at_100.low == '':
            return 0
        elif self.viscosity_at_100.high == None or self.viscosity_at_100.high == '':
            return 0
        else:
            # assuming here that the values are valid
            try:
                return (int(self.viscosity_at_100.high) - int(self.viscosity_at_100.low))/2
            except ValueError:
                print("Invalid viscosity values for product {0}".format(self.material_code))
                print("Viscosity at 100 low = " +str(self.viscosity_at_100.low))
                print("Viscosity at 100 high = " +str(self.viscosity_at_100.high))
                return 0

    def calculate_average_viscosity_at_40(self):
        if self.viscosity_at_40.low == None or self.viscosity_at_40.low == '':
            return 0
        elif self.viscosity_at_40.high == None or self.viscosity_at_40.high == '':
            return 0
        else:
            # assuming here that the values are valid
            try:
                return (int(self.viscosity_at_40.high) - int(self.viscosity_at_40.low))/2
            except ValueError:
                print("Invalid viscosity values for product {0}".format(self.material_code))
                print("Viscosity at 100 low = " +str(self.viscosity_at_100.low))
                print("Viscosity at 100 high = " +str(self.viscosity_at_100.high))
                return 0
