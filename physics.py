import numpy as np

# Universal gravitational constant (SI units)
G = 6.67430e-11

# Mass of Earth in kilograms
EARTH_MASS = 5.972e24

# Mean radius of Earth in meters
EARTH_RADIUS = 6_371_000


def gravitational_acceleration(position):
    # Calculate the distance from Earth's center
    distance = np.linalg.norm(position)
    if distance == 0:
        raise ValueError("Position cannot be zero")

    # Gravitational acceleration: a = -G * M * r / |r|^3
    acceleration = -G * EARTH_MASS * position / distance**3
    return acceleration