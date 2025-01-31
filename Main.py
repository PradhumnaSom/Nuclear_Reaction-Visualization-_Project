import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation
from matplotlib.widgets import Button

# Constants
num_particles = 700
radius = 5
simulation_started = False
process_type = 'fission'
split_triggered = False
frame_count = 0

# Particle arrays
fragment_positions = np.zeros((num_particles, 3))
fragment_velocities = np.zeros((num_particles, 6))

# Uranium's initial position and velocity
uranium_position = np.array([-radius * 5, 0, 0], dtype=float)
uranium_velocity = np.array([0.9, 0, 0])  # Traveling along the x-axis

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

# Button axes
button_ax_start = fig.add_axes([0.35, 0.02, 0.1, 0.05])  # [left, bottom, width, height] for Start button
button_ax_reset = fig.add_axes([0.46, 0.02, 0.1, 0.05])  # [left, bottom, width, height] for Reset button

# Create buttons
start_button = Button(button_ax_start, 'Start', color='lightgreen', hovercolor='lime')
reset_button = Button(button_ax_reset, 'Reset', color='lightblue', hovercolor='dodgerblue')

# Text message for the start prompt
start_text = ax.text(0.5, 0.5, 0, 'Press Space to Start', color='white', fontsize=15, ha='center', va='center')

# Neon-like glowing effect for fragments
neon_colors = np.array([
    np.random.uniform(0.2, 1.0, num_particles),  # Red
    np.random.uniform(0.2, 1.0, num_particles),  # Green
    np.random.uniform(0.2, 1.0, num_particles)   # Blue
]).T

# Create a glowing effect by using a larger dot with a soft alpha transparency for outer particles
def create_glow_effect():
    # Create an outline with softer glow (larger particles with lower transparency)
    glow_effect = ax.scatter([], [], [], s=30, color='white', alpha=0.3)  # White glowing effect
    return glow_effect

glow_effect = create_glow_effect()

def init():
    ax.set_xlim([-radius * 3, radius * 3])
    ax.set_ylim([-radius * 3, radius * 3])
    ax.set_zlim([-radius * 3, radius * 3])
    #ax.set_axis_off()  # Hides the axes entirely

    # Set initial positions
    sc_uranium._offsets3d = ([], [], [])
    sc_stationary._offsets3d = ([], [], [])
    sc_fragments._offsets3d = ([], [], [])
    glow_effect._offsets3d = ([], [], [])
    return sc_uranium, sc_stationary, sc_fragments, glow_effect


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

            # Create glowing effect for the fragments
            glow_effect._offsets3d = (fragment_positions[:, 0], fragment_positions[:, 1], fragment_positions[:, 2])

            # Update particle colors to a neon-like glow effect
            sc_fragments.set_facecolor(neon_colors)

            sc_fragments.set_sizes(np.full(num_particles, 10))
            sc_uranium._offsets3d = ([], [], [])  # Hide uranium after collision
            sc_stationary._offsets3d = ([], [], [])  # Hide stationary atom after collision

    return sc_uranium, sc_stationary, sc_fragments, glow_effect


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
    glow_effect._offsets3d = ([], [], [])
    fig.canvas.draw_idle()

    # Show start text again after reset
    start_text.set_visible(True)


def start(event):
    """Start the simulation when the Start button is pressed."""
    global simulation_started
    simulation_started = True
    # Hide the start text once the simulation starts
    start_text.set_visible(False)


def on_key_press(event):
    """Start the simulation when the spacebar is pressed."""
    global simulation_started
    if event.key == ' ':
        simulation_started = True
        # Hide the start text once the spacebar is pressed
        start_text.set_visible(False)


# Connect buttons to functions
start_button.on_clicked(start)
reset_button.on_clicked(reset)

# Connect the key press event to the function
fig.canvas.mpl_connect('key_press_event', on_key_press)

# Create animation
ani = animation.FuncAnimation(fig, update, frames=200, init_func=init, blit=False, interval=50)

plt.show()
