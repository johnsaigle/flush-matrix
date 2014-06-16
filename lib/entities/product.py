from collections import namedtuple
class Product:
    def __init__(self, name, material_code, description, elemental_values, demulse_test, family_group, viscosity_at_40_low=None, vicsosity_at_40_high=None,viscosity_at_100_low =None, viscsoity_at_100_high=None):
        self.name = name
        self.material_code = material_code # a numerical product code
        self.description = description
        self.family_group = family_group # string representing a group code
        self.elemental_values = {} # dictionary mapping the names of elements to their percentage value
        self.demulse_test = demulse_test # enum of separation, meld, or n/a depending on the product
        Viscosity = namedtuple('Viscosity', 'low high')
        viscosity_at_40 = Viscosity(viscosity_at_40_low, viscosity_at_40_high)
        viscosity_at_100 = Viscosity(viscosity_at_100_low, viscosity_at_100_high)

