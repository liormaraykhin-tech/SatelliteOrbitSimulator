import numpy as np

from physics import EARTH_RADIUS , G , EARTH_MASS
from simulation import simulate
from visualization import plot_energy_error ,plot_orbit

# Initial satellite position in meters (X, Y, Z)
position = np.array([7_000_000, 0, 0])

# Calculate the required speed for a circular orbit
# Formula: v_circular = sqrt(G * M / r)
# G = gravitational constant, M = Earth's mass, r = orbital radius
circular_speed=np.sqrt(G*EARTH_MASS/np.linalg.norm(position))


# Allow the user to select an orbital configuration
# Available presets: circular, elliptical, and high-eccentricity orbit
orbit_type=input("Choose orbit (circular / elliptical / high): ")
print(orbit_type)


# Select the initial orbital speed based on the chosen preset
# Circular: v = sqrt(G * M / r)
# Elliptical: v = 7500 m/s (slightly below circular speed)
# High: v = 7900 m/s (above circular speed, below escape speed)
# Escape speed formula: v_escape = sqrt(2 * G * M / r)
if orbit_type=="circular":
    initial_speed=circular_speed
elif orbit_type=="elliptical":
    initial_speed=7500
elif orbit_type=="high":
    initial_speed = 7900
else:
    raise ValueError("Invalid orbit type")





# Define the initial velocity vector in meters per second (X, Y, Z)
# The satellite starts moving along the positive Y-axis
# Velocity vector: v = (0, initial_speed, 0)
velocity = np.array([0,initial_speed , 0])



# Calculate the initial orbital radius from Earth's center
# Calculate the semi-major axis using the vis-viva equation
# Formula: a = 1 / (2/r - v^2/(G*M))
initial_radius=np.linalg.norm(position)
semi_major_axis=1/((2/initial_radius)-(initial_speed*initial_speed)/(G*EARTH_MASS))

# Define the simulation time step and total duration
dt = 1.0

# Calculate the orbital period using Kepler's third law
# Formula: T = 2*pi*sqrt(a^3/(G*M))
# a = semi-major axis of the orbit
orbital_period=2*np.pi*np.sqrt(semi_major_axis**3/(G*EARTH_MASS))
simulation_time=orbital_period

# Display the orbital period in minutes
print(f"Orbital Period: {orbital_period / 60:.2f} minutes")

steps = int(simulation_time / dt)
positions , velocities =simulate(steps,dt,velocity,position)

# Convert the stored satellite positions into a NumPy array
positions_array=np.array(positions)
velocities_array=np.array(velocities)

# Calculate the satellite's distance from Earth's center and speed at each time step
distances=np.linalg.norm(positions_array,axis=1)
speeds = np.linalg.norm(velocities_array,axis=1)

# Calculate the satellite's specific kinetic energy (v² / 2)
# and gravitational potential energy (-GM / r) at each time step
kinetic_energy=np.square(speeds)/2
potential_energy=-G*EARTH_MASS/distances

# Calculate total specific mechanical energy to verify energy conservation
total_energy=kinetic_energy + potential_energy

# Use the initial mechanical energy as a reference for measuring numerical error
initial_energy=total_energy[0]

# Calculate the change in mechanical energy relative to the initial state
energy_difference=total_energy-initial_energy

# Calculate the absolute relative energy error as a percentage
relative_energy_error=np.abs((energy_difference/initial_energy)*100)




# Generate time values in seconds for each recorded simulation state
times=np.arange(0,steps+1,1)*dt

energy_fig=plot_energy_error(times,relative_energy_error)

# Find the minimum and maximum distance from Earth's center
min_distance=np.min(distances)
max_distance=np.max(distances)
perigee_index=np.argmin(distances)
apogee_index=np.argmax(distances)
perigee_position=positions_array[perigee_index]
apogee_position=positions_array[apogee_index]


# Calculate the minimum and maximum altitude above Earth's surface
# Minimum altitude (Perigee)
perigee_altitude=(min_distance-EARTH_RADIUS)/1000
# Maximum altitude (Apogee)
apogee_altitude=(max_distance-EARTH_RADIUS)/1000

# Display orbital altitude for circular orbits
# and perigee/apogee altitudes for elliptical orbits
if orbit_type != "circular":
    print(f"Perigee Altitude: {perigee_altitude:.2f} km")
    print(f"Apogee Altitude:  {apogee_altitude:.2f} km")
else:
    print(f"Orbital Altitude: {perigee_altitude:.2f} km")

fig=plot_orbit(positions_array,EARTH_RADIUS,perigee_position,apogee_position, perigee_altitude, apogee_altitude,orbit_type, orbital_period)

# Display the 3D satellite orbit visualization
fig.show()
energy_fig.show()
