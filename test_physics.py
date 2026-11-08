import numpy as np
from simulation import simulate
from physics import gravitational_acceleration , G , EARTH_MASS

def test_gravity_direction():
    # Gravity should always point toward the center of the Earth.
    # If the satellite is on the positive X-axis, its gravitational
    # acceleration must point in the negative X direction.

    position=np.array([7000000,0,0])
    acceleration=gravitational_acceleration(position)

    # The X component must be negative, while Y and Z must be zero.
    assert (acceleration[0]<0 and acceleration[1]==0 and acceleration[2]==0)

def test_gravity_magnitude():
    # Newton's law of gravitation gives the acceleration:
    # a = G * M / r^2
    #
    # At a distance of 7,000 km from Earth's center,
    # the expected gravitational acceleration is about 8.13 m/s^2.
    #
    # We allow a small tolerance of 0.01 m/s^2.

    position=np.array([7000000,0,0])
    acceleration = gravitational_acceleration(position)
    assert(np.isclose(np.linalg.norm(acceleration),8.13,atol=0.01))

def test_energy_conservation():
    # A satellite moving under Earth's gravity should conserve
    # its total mechanical energy.
    #
    # We use specific orbital energy (energy per unit mass),
    # so we do not need to know the satellite's mass.
    #
    # Specific kinetic energy:   Ek = v^2 / 2
    # Specific potential energy: Ep = -G * M / r
    # Total specific energy:     E = Ek + Ep

    # Define the initial position and velocity.
    initial_position=np.array([7000000,0,0])
    initial_velocity=np.array([0,7500,0])

    # Simulate the satellite's motion for 5820 seconds
    # using a time step of 1 second.
    positions, velocities=simulate(5820,1.0,initial_velocity,initial_position)

    # Calculate the initial kinetic energy per unit mass.
    v0=np.linalg.norm(initial_velocity)
    kinetic_energy=v0*v0/2

    # Calculate the initial gravitational potential energy
    # per unit mass using the distance from Earth's center.
    r0=np.linalg.norm(initial_position)
    potential_energy =-G*EARTH_MASS/r0

    # Add both energy components to get the initial total energy.
    initial_energy=kinetic_energy+potential_energy

    # Get the satellite's final speed and distance from Earth.
    final_velocity=np.linalg.norm(velocities[-1])
    final_radius=np.linalg.norm(positions[-1])
    # Calculate the final kinetic and potential energies.
    final_kinetic_energy=final_velocity*final_velocity*0.5
    final_potential_energy=-G*EARTH_MASS/final_radius

    # Calculate the total energy at the end of the simulation.
    final_energy=final_kinetic_energy+final_potential_energy

    # Measure how much the energy changed relative to its
    # initial value.
    #
    # Relative error = |(E_final - E_initial) / E_initial|
    #
    # A small error indicates that the numerical simulation
    # preserves energy accurately between these two points.
    relative_error=abs(final_energy-initial_energy)/abs(initial_energy)
    # Accept a relative energy error smaller than 0.001%.
    assert (relative_error < 1e-5)

def test_angular_momentum_conservation():
    # Angular momentum should remain constant because Earth's gravity
    # acts toward the center of the Earth and produces no torque.
    #
    # Specific angular momentum: h = r x v
    # We calculate its magnitude at the beginning and end of the simulation.
    #
    # The relative error must be smaller than 1e-5 (0.001%).
    position=np.array([7000000,0,0])
    velocity=np.array([0,7500,0])
    dt=1.0
    steps=5820
    positions, velocities = simulate(steps,dt,velocity,position)

    # Calculate the specific angular momentum vectors
    # at the beginning and end of the simulation.
    h_initial=np.cross(positions[0],velocities[0])
    h_final=np.cross(positions[-1],velocities[-1])

    # Calculate the magnitude of each angular momentum vector.
    h_initial_magnitude=np.linalg.norm(h_initial)
    h_final_magnitude=np.linalg.norm(h_final)

    # Calculate the relative change in angular momentum.
    # Verify that the numerical error stays below 0.001%.
    relative_error=abs(h_final_magnitude-h_initial_magnitude)/h_initial_magnitude
    assert (relative_error < 1e-5)

def test_circular_orbit():
    # Verify that a satellite with the correct circular orbital velocity
    # returns close to its starting position after one complete orbit.
    radius=7000000

    # Calculate the required circular orbital speed using Newtonian gravity.
    # v = sqrt(G * M / r)
    circular_speed=np.sqrt(G*EARTH_MASS/radius)

    # Set the initial position and a perpendicular velocity
    # to produce a circular orbit.
    initial_position=np.array([radius,0,0])
    initial_velocity=np.array([0,circular_speed,0])

    # Calculate the theoretical orbital period and convert it
    # into the nearest whole number of simulation steps.
    orbital_period=2*np.pi*radius/circular_speed
    dt=1.0
    steps=round(orbital_period/dt)

    # Simulate one complete orbit using the Velocity Verlet method.
    positions, velocities = simulate(steps, dt, initial_velocity, initial_position)

    # Measure the distance between the final and initial positions.
    # Accept a return distance smaller than 10 km.
    return_distance=np.linalg.norm(positions[-1]-initial_position)
    assert return_distance<10000

    # Calculate the distance from Earth's center at every simulation step.
    # In a perfect circular orbit, this distance should remain constant.
    radii=[np.linalg.norm(position) for position in positions]

    # Find the largest absolute deviation from the expected orbital radius.
    max_deviation=max(abs(r-radius) for r in radii)

    # Verify that the orbital radius never deviates by 100 meters or more.
    # This confirms that the simulated orbit remains nearly circular.
    assert(max_deviation<100)

def test_dt_sensitivity():
    # Compare two simulations with different time steps
    # to evaluate the numerical sensitivity of the orbital trajectory.
    initial_position=np.array([7000000,0,0])
    initial_velocity=np.array([0,7500,0])
    simulation_time=5820
    dt_small=1.0
    dt_large=5.0

    # Calculate the number of steps required to simulate
    # the same total duration with each time step.
    steps_small=int(simulation_time/dt_small)
    steps_large=int(simulation_time/dt_large)

    # Run both simulations using identical initial conditions
    # but different time step sizes.
    positions_small , velocities_small =simulate(steps_small, dt_small, initial_velocity, initial_position)
    positions_large , velocities_large =simulate(steps_large, dt_large, initial_velocity, initial_position)

    # Measure the distance between the final positions
    # of the two simulated trajectories.
    final_position_difference=np.linalg.norm(positions_large[-1]-positions_small[-1])

    # Verify that the final position difference remains below 500 meters.
    assert final_position_difference<500

def test_output_validity():
    # Verify that the simulation returns valid and consistent output.
    # Check array lengths, numerical values, and initial conditions.
    initial_position=np.array([7000000,0,0])
    initial_velocity=np.array([0,7500,0])
    dt=1.0
    steps=100

    # Run a short simulation to validate the returned data.
    positions, velocities = simulate(steps, dt, initial_velocity, initial_position)

    # Each output must contain the initial state plus one entry per step.
    assert(len(positions)==steps+1)
    assert(len(velocities)==steps+1)

    # Ensure all position and velocity values are finite.
    # Reject NaN and positive or negative infinity.
    assert(np.all(np.isfinite(positions)))
    assert(np.all(np.isfinite(velocities)))

    # Verify that the first stored state matches the initial conditions.
    assert(np.array_equal(positions[0],initial_position))
    assert(np.array_equal(velocities[0],initial_velocity))

