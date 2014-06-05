class Product:
    def __init__(self, material_code, name, family_group, density=None, viscosity_range=None, viscosity_specs_at_40 = None, viscosity_specs_at_100 = None, sensitivity=None):
        self.material_code = material_code # a numerical product code
        self.name = name
        self.family_group = family_group
        self.density= density # int; physical property of product
        self.viscosity_range = viscosity_range # tuple type: Low, High, Typ
        self.viscosity_specs_at_40 = viscosity_specs_at_40 # tuple type: Low, High, Typ
        self.viscosity_specs_at_100 = viscosity_specs_at_100 # tuple type: Low, High, Typ 
        self.sensitivity = sensitivity # strings representing special notes about the product
        self.elemental_values = {}
