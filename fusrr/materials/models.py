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
class MaterialValueZeroToOne:
    value: float

    def __post_init__(self):
        if self.value < 0 or self.value > 1:
            raise ValueError("Value must be between 0 and 1.")

    @property
    def tup(self):
        """Return the vector as a tuple."""
        return self.value
