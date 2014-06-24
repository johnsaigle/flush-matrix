class Equipment:
    def __init__(self, name, area, residual_volume, cycle_size, flush_material, initial_fill_size=None):
        self.name = name # string representation of equipment line
        self.area = area # string; a department of the plant (packaging, blending...)
        self.residual_volume = int(residual_volume)
        self.cycle_size = int(cycle_size) # typical flush size to clean a container. This is a default value to be multipled as determined by the flush_matrix script
        self.flush_material = flush_material # the product used in the flushing
        self.initial_fill_size = int(initial_fill_size)

    
