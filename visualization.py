import numpy as np
import plotly.graph_objects as go
from PIL import Image


def plot_energy_error(times,relative_energy_error):
    energy_fig=go.Figure()
    energy_trace=go.Scatter(x=times,y=relative_energy_error,mode="lines")
    energy_fig.add_trace(energy_trace)
    energy_fig.update_layout(title="Energy Conservation Error", xaxis_title="Time (seconds)",yaxis_title="Relative Energy Error (%)" ,title_x=0.5)
    return (energy_fig)


def plot_orbit(positions_array,earth_radius, perigee_position,apogee_position,perigee_altitude,apogee_altitude,orbit_type,orbital_period):
    x_positions=positions_array[:,0]
    y_positions=positions_array[:,1]
    z_positions=positions_array[:,2]
    start_x=positions_array[0][0]
    start_y = positions_array[0][1]
    start_z = positions_array[0][2]
    orbit=go.Scatter3d(
        x=x_positions,
        y=y_positions,
        z=z_positions,
        mode="lines",
        name="Orbit Path",
    )
    fig = go.Figure()
    fig.add_trace(orbit)

    # Sample every 50th position to create animation frames
    animation_positions=positions_array[::50]

    satellite_position = positions_array[0]

    # Store the animation frames
    frames=[]

    # Generate the satellite body and solar panels for each frame
    for position in animation_positions:
        satellite_body, right_panel, left_panel=create_satellite(position,200000)

        # Update only the three satellite traces in each frame
        frame = go.Frame(data=[satellite_body, right_panel, left_panel] , traces = [1,2,3])
        frames.append(frame)

    # Create and display the satellite body at its initial orbital position
    satellite_body, right_panel, left_panel = create_satellite(satellite_position, 200000)
    fig.add_trace(satellite_body)
    fig.add_trace(right_panel)
    fig.add_trace(left_panel)
    # Generate angular values for the Earth's spherical surface
    alpha = np.linspace(0, 2 * np.pi, 400)
    theta = np.linspace(0, np.pi, 200)
    # Create a 2D grid containing all combinations of the two angles
    alpha_grid, theta_grid = np.meshgrid(alpha, theta)
    # Calculate the X, Y, and Z coordinates of the Earth's surface
    x_earth = earth_radius * np.cos(alpha_grid) * np.sin(theta_grid)
    y_earth = earth_radius * np.sin(alpha_grid) * np.sin(theta_grid)
    z_earth = earth_radius * np.cos(theta_grid)

    # Flatten the 2D coordinate grids into 1D arrays for Mesh3d
    earth_x_flat=x_earth.flatten()
    earth_y_flat=y_earth.flatten()
    earth_z_flat=z_earth.flatten()

    # Store the vertex indices that define Earth's triangular mesh
    # Each grid cell is divided into two triangles
    triangles_i=[]
    triangles_j=[]
    triangles_k=[]
    for row in range(199):
        for col in range(399):
            a_index=row*400+col
            b_index=a_index+1
            c_index=a_index+400
            d_index=c_index+1
            triangles_i.append(a_index)
            triangles_j.append(b_index)
            triangles_k.append(c_index)
            triangles_i.append(b_index)
            triangles_j.append(d_index)
            triangles_k.append(c_index)

    # Create Earth's 3D surface using Plotly
    # Load and resize the Earth texture to match the mesh resolution
    earth_image = Image.open("earth_texture.jpg")
    earth_image = earth_image.resize((400, 200), Image.Resampling.LANCZOS)
    earth_pixels=np.asarray(earth_image)

    # Reshape the image into one RGB triplet per mesh vertex
    earth_colors = earth_pixels.reshape(-1, 3)

    # Convert RGB pixel values into Plotly-compatible color strings
    # Store each color for later use in the 3D mesh
    vertex_colors=[]
    for item in earth_colors:
        color = f"rgb({item[0]},{item[1]},{item[2]})"
        vertex_colors.append(color)

    # Build Earth's 3D mesh from vertex coordinates and triangle indices
    # The texture colors will be assigned to individual vertices
    earth = go.Mesh3d(x=earth_x_flat, y=earth_y_flat, z=earth_z_flat ,i=triangles_i , k=triangles_k, j=triangles_j , vertexcolor=vertex_colors)



    # Add Earth's surface to the 3D figure
    fig.add_trace(earth)
    start_marker=go.Scatter3d(
        x=[start_x],
        y=[start_y],
        z=[start_z],
        name="START",
        mode="markers+text",
        text=["START"],
        marker=dict(color="lime", size=8),
        textfont=dict(color="#A3FFB0", size=15),
        textposition="middle left",
    )
    fig.add_trace(start_marker)

    # Mark the satellite's minimum altitude along the orbit
    perigee_marker=go.Scatter3d(x=[perigee_position[0]] ,
                                y=[perigee_position[1]],
                                z=[perigee_position[2]],
                                name="PERIGEE",
                                mode="markers+text",
                                text=[f"PERIGEE — {perigee_altitude:.2f} km"],
                                textfont=dict(color="cyan", size=13),
                                textposition="bottom left",
                                marker=dict(color="cyan" , size=8),
                                )

    # Mark the satellite's maximum altitude along the orbit
    apogee_marker=go.Scatter3d(x=[apogee_position[0]] ,
                                y=[apogee_position[1]],
                                z=[apogee_position[2]],
                                name="APOGEE",
                                mode="markers+text",
                               text=[f"APOGEE — {apogee_altitude:.2f} km"],
                               textfont=dict(color="orange", size=13),
                               textposition="bottom left",
                                marker=dict(color="orange" , size=8),
                                )
    # Display perigee and apogee markers only for non-circular orbits
    if orbit_type!="circular":
        fig.add_trace(apogee_marker)
        fig.add_trace(perigee_marker)


    # Configure the 3D plot layout and axis proportions
    fig.update_layout(
        title=f"Satellite Orbit Simulator — {orbit_type.upper()} | Orbital Period: {orbital_period / 60:.2f} min",
        title_x=0.5,
        scene=dict(aspectmode="data" ,
                   bgcolor="#152238",
                   xaxis=dict(showbackground=False),
                   yaxis=dict(showbackground=False),
                   zaxis=dict(showbackground=False),
                   )
    )

    # Attach the animation frames to the 3D figure
    fig.frames=frames

    # Add playback controls for the satellite animation
    fig.update_layout(updatemenus=[
                      dict(
                      type="buttons",
                      buttons=[
                          # Play the animation with a 100 ms frame duration
                          dict(
                              label="Play",
                              method="animate",
                              args=[None,dict(frame=dict(duration=100,redraw=True)) ],
                          ),

                          # Configure the pause button to stop the animation
                          dict(label="Pause",method="animate", args=[[None ], dict(mode="immediate",frame=dict(duration=0, redraw=False), transition=dict(duration=0))]),
                      ],
                      )
        ]
    )
    return (fig)


def create_satellite(position,size):
    # Extract the satellite's center coordinates
    x=position[0]
    y=position[1]
    z=position[2]

    # Calculate half the cube's side length
    half_size=size/2.0
    panel_length=2*size
    panel_width=0.8*size

    # Define the coordinates of the cube's eight vertices
    cube_x=[x-half_size,x-half_size,x-half_size,x-half_size,x+half_size,x+half_size,x+half_size,x+half_size]
    cube_y=[y-half_size,y+half_size,y+half_size,y-half_size,y-half_size,y+half_size,y+half_size,y-half_size]
    cube_z=[z-half_size,z-half_size,z+half_size,z+half_size,z-half_size,z-half_size,z+half_size,z+half_size]

    # Build the satellite body using 12 triangles forming six faces
    body=go.Mesh3d(x=cube_x,
                   y=cube_y,
                   z=cube_z,
                   color="silver" ,
                   i=[0, 0,4 , 4, 0, 0, 3, 3, 0, 0, 1, 1],
                   j=[1, 2, 6, 7, 4, 5, 2, 6, 3, 7, 5 ,6],
                   k=[2, 3, 5 ,6, 5, 1, 6, 7, 7, 4, 6 , 2],

    )
    right_panel_x=[x + half_size,x + half_size,x + half_size + panel_length,x + half_size + panel_length]
    panel_y=[y - panel_width / 2,y + panel_width / 2,y + panel_width / 2 ,y - panel_width / 2]
    panel_z=4*[z]
    left_panel_x=[x - half_size, x - half_size,x - half_size - panel_length,x - half_size - panel_length]
    right_panel=go.Mesh3d(x=right_panel_x,
                          y=panel_y,
                          z=panel_z,
                          color="royalblue",
                          i = [0, 0],
                          j = [1, 2],
                          k = [2, 3],
    )
    left_panel = go.Mesh3d(x=left_panel_x,
                            y=panel_y,
                            z=panel_z,
                            color="royalblue",
                            i=[0, 0],
                            j=[1, 2],
                            k=[2, 3],
                            )
    # Return the satellite body and both solar panels
    return body ,right_panel,left_panel


