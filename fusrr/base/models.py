from attr import dataclass


@dataclass
class Vec2:
    x: float
    y: float

    @classmethod
    @property
    def ONE(cls):
        return cls(1, 1)

    @classmethod
    @property
    def ZERO(cls):
        return cls(0, 0)

    @classmethod
    @property
    def X(cls):
        return cls(1, 0)

    @classmethod
    @property
    def Y(cls):
        return cls(0, 1)

    @property
    def tup(self):
        return (self.x, self.y)

    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vec2(self.x - other.x, self.y - other.y)

    def dot(self, other):
        return self.x * other.x + self.y * other.y


@dataclass
class Vec3:
    x: float
    y: float
    z: float

    @classmethod
    @property
    def ONE(cls):
        return cls(1, 1, 1)

    @classmethod
    @property
    def ZERO(cls):
        return cls(0, 0, 0)

    @classmethod
    @property
    def X(cls):
        return cls(1, 0, 0)

    @classmethod
    @property
    def Y(cls):
        return cls(0, 1, 0)

    @classmethod
    @property
    def Z(cls):
        return cls(0, 0, 1)

    @property
    def tup(self):
        return (self.x, self.y, self.z)

    def __add__(self, other):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def dot(self, other):
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other):
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )
