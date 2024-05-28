from dataclasses import dataclass


@dataclass
class MaterialColour:
    # entering the RGB value for colours
    # each value is between 0-1, which is scalled down from the normal 0-255
    r: float
    g: float
    b: float
    alpha: float

    @property
    def tup(self):
        """Return the vector as a tuple."""
        return (self.r, self.g, self.b, self.alpha)
    
@dataclass
class MaterialRoughness:
    # entering the roughness value (between 0-1) for material
    roughness_val: float

    @property
    def tup(self):
        """Return the vector as a tuple."""
        return (self.roughness_val)
    
@dataclass
class MaterialMetallic:
    # entering the metallic value (between 0-1) for material 
    metallic_val: float

    @property
    def tup(self):
        """Return the vector as a tuple."""
        return (self.metallic_val)