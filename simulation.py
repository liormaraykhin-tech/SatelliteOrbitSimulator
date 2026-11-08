import numpy as np

from physics import gravitational_acceleration


def simulate(steps,dt,initial_velocity,initial_position):
    initial_position=np.array(initial_position ,dtype=float)
    position = initial_position.copy()
    velocity = np.array(initial_velocity, dtype=float)
    velocities= []
    positions = []
    positions.append(initial_position.copy())
    velocities.append(velocity.copy())

    for _ in range(steps):
        acceleration=gravitational_acceleration(position)
        new_position=position+velocity*dt+0.5*acceleration*dt*dt
        new_acceleration=gravitational_acceleration(new_position)
        new_velocity=velocity+(new_acceleration+acceleration)*dt*0.5
        position=new_position
        velocity=new_velocity
        velocities.append(velocity.copy())
        positions.append(position.copy())

    return (positions,velocities)




