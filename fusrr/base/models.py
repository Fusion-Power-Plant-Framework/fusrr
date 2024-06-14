from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


class staticproperty:  # noqa: N801
    def __init__(self, func):
        self.fget = func

    def __get__(self, _instance, _owner):
        return self.fget()


class classproperty:  # noqa: N801
    def __init__(self, func):
        self.fget = func

    def __get__(self, _instance, owner):
        return self.fget(owner)


@dataclass
class Vec2:
    """A vector in R2."""

    x: float
    y: float

    @staticproperty
    def ONE() -> Vec2:
        """Return the one vector."""
        return Vec2(1, 1)

    @staticproperty
    def ZERO() -> Vec2:
        """Return the zero vector."""
        return Vec2(0, 0)

    @staticproperty
    def X() -> Vec2:
        """Return the X axis."""
        return Vec2(1, 0)

    @staticproperty
    def Y() -> Vec2:
        """Return the Y axis."""
        return Vec2(0, 1)

    @property
    def tup(self):
        """Return the vector as a tuple."""
        return (self.x, self.y)

    def __add__(self, other: Vec2):
        return Vec2(self.x + other.x, self.y + other.y)

    def __sub__(self, other: Vec2):
        return Vec2(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar: float):
        return Vec2(self.x * scalar, self.y * scalar)

    def dot(self, other: Vec2):
        """Return the dot product of this vector and another."""
        return self.x * other.x + self.y * other.y


@dataclass(eq=True, frozen=True, repr=True)
class Vec3:
    """A vector in R3."""

    x: float
    y: float
    z: float

    @staticproperty
    def ONE() -> Vec3:
        """Return the one vector."""
        return Vec3(1, 1, 1)

    @staticproperty
    def ZERO() -> Vec3:
        """Return the zero vector."""
        return Vec3(0, 0, 0)

    @staticproperty
    def X() -> Vec3:
        """Return the X axis."""
        return Vec3(1, 0, 0)

    @staticproperty
    def Y() -> Vec3:
        """Return the Y axis."""
        return Vec3(0, 1, 0)

    @staticproperty
    def Z() -> Vec3:
        """Return the Z axis."""
        return Vec3(0, 0, 1)

    @property
    def tup(self):
        """Return the vector as a tuple."""
        return (self.x, self.y, self.z)

    def __add__(self, other: Vec3):
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: Vec3):
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, scalar: float):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def dot(self, other: Vec3):
        """Return the dot product of this vector and another."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: Vec3):
        """Return the cross product of this vector and another."""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x,
        )
