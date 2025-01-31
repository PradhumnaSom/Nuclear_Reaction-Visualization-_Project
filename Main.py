import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.widgets import Button

# Constants
num_particles = 100
radius = 10
simulation_started = False
process_type = 'fission'
split_triggered = False
frame_count = 0

# Particle arrays
fragment_positions = np.zeros((num_particles, 3))
fragment_velocities = np.zeros((num_particles, 3))

# Uranium's initial position and velocity
uranium_position = np.array([-radius * 2, 0, 0], dtype=float)
uranium_velocity = np.array([0.5, 0, 0])  # Traveling along the x-axis

# Stationary atom's position
stationary_atom_position = np.array([0, 0, 0])

# Create figure and axis
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.set_facecolor('black')

# Scatter objects
sc_uranium = ax.scatter([], [], [], s=100, color='green')  # Uranium atom
sc_stationary = ax.scatter([], [], [], s=150, color='red')  # Stationary atom
sc_fragments = ax.scatter([], [], [], s=10, color='cyan')  # Fragments

# Button axis
button_ax = fig.add_axes([0.8, 0.02, 0.1, 0.05])  # [left, bottom, width, height]
reset_button = Button(button_ax, 'Reset', color='lightblue', hovercolor='dodgerblue')


def init():
    ax.set_xlim([-radius * 3, radius * 3])
    ax.set_ylim([-radius * 3, radius * 3])
    ax.set_zlim([-radius * 3, radius * 3])

    # Set initial positions
    sc_uranium._offsets3d = ([], [], [])
    sc_stationary._offsets3d = ([], [], [])
    sc_fragments._offsets3d = ([], [], [])
    return sc_uranium, sc_stationary, sc_fragments


def update(frame):
    global simulation_started, split_triggered, frame_count, fragment_positions, fragment_velocities, uranium_position

    if simulation_started:
        if not split_triggered:
            # Move uranium atom toward the stationary atom
            uranium_position += uranium_velocity
            sc_uranium._offsets3d = ([uranium_position[0]], [uranium_position[1]], [uranium_position[2]])
            sc_stationary._offsets3d = ([stationary_atom_position[0]], [stationary_atom_position[1]], [stationary_atom_position[2]])

            # Check for collision
            if np.linalg.norm(uranium_position - stationary_atom_position) < 1.0:
                split_triggered = True
                # Generate random spherical directions for fragments
                theta = np.random.uniform(0, 2 * np.pi, num_particles)
                phi = np.random.uniform(0, np.pi, num_particles)
                speed = 0.5
                vx = speed * np.sin(phi) * np.cos(theta)
                vy = speed * np.sin(phi) * np.sin(theta)
                vz = speed * np.cos(phi)
                fragment_velocities = np.array([vx, vy, vz]).T
        else:
            # Simulate fragments after collision
            fragment_positions += fragment_velocities
            sc_fragments._offsets3d = (fragment_positions[:, 0], fragment_positions[:, 1], fragment_positions[:, 2])
            sc_fragments.set_sizes(np.full(num_particles, 10))
            sc_uranium._offsets3d = ([], [], [])  # Hide uranium after collision
            sc_stationary._offsets3d = ([], [], [])  # Hide stationary atom after collision

    return sc_uranium, sc_stationary, sc_fragments


def reset(event):
    """Reset the simulation to its initial state."""
    global simulation_started, split_triggered, frame_count, fragment_positions, fragment_velocities, uranium_position
    simulation_started = False
    split_triggered = False
    frame_count = 0
    fragment_positions.fill(0)
    fragment_velocities.fill(0)
    uranium_position = np.array([-radius * 2, 0, 0], dtype=float)

    # Reset scatter plot data
    sc_uranium._offsets3d = ([], [], [])
    sc_stationary._offsets3d = ([], [], [])
    sc_fragments._offsets3d = ([], [], [])
    fig.canvas.draw_idle()


# Connect the reset button to the reset function
reset_button.on_clicked(reset)


def on_key_press(event):
    """Start the simulation when the spacebar is pressed."""
    global simulation_started
    if event.key == ' ':
        simulation_started = True


# Connect the key press event to the function
fig.canvas.mpl_connect('key_press_event', on_key_press)

# Create animation
ani = animation.FuncAnimation(fig, update, frames=200, init_func=init, blit=False, interval=50)

plt.show()
