import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FFMpegWriter
from matplotlib.ticker import MaxNLocator

"""We need to preprocess the array for the deleted particle coordinates to make it suitable for histogram movie."""


def load_data(data_path, sim_params_path):
    data = np.load(data_path)
    sim_params = np.load(sim_params_path)
    return data, sim_params


def combine_coordinates(data):
    combined_data = []
    current_timestep = None
    current_coordinates = []

    for row in data:
        timestep, coordinates = row
        if current_timestep is None:
            current_timestep = timestep

        if timestep == current_timestep:
            current_coordinates.append(coordinates)
        else:
            # Combine the coordinates for the current timestep into a single row
            combined_row = [current_timestep] + current_coordinates
            combined_data.append(combined_row)

            # Reset variables for the new timestep
            current_timestep = timestep
            current_coordinates = [coordinates]

    # Append the last timestep's data
    if current_timestep is not None:
        combined_row = [current_timestep] + current_coordinates
        combined_data.append(combined_row)

    return combined_data


def accumulate_data(data):
    processed_data = []
    elements_seen = []

    for row in data:
        # Extract all elements except the first one (assuming the first one is x-value)
        current_elements = row[1:]

        # Update the list of seen elements
        for element in current_elements:
            if element not in elements_seen:
                elements_seen.append(element)

        # Create a new data point with the x value and the accumulated elements
        new_data_point = [row[0]] + elements_seen.copy()
        processed_data.append(new_data_point)

    return processed_data


def fill_missing_timesteps(data, timestep_interval, start_value, final_timestep):
    if not data:
        return []

    filled_data = []
    current_timestep = 0

    # Fill from 0 to the first data timestep
    while current_timestep < data[0][0]:
        filled_data.append([current_timestep] + [start_value])
        current_timestep += timestep_interval

    last_row = data[0]
    filled_data.append(last_row)

    # Fill in gaps within the original data
    for i in range(1, len(data)):
        current_row = data[i]
        current_timestep = last_row[0] + timestep_interval

        while current_timestep < current_row[0]:
            filled_data.append([current_timestep] + last_row[1:])
            current_timestep += timestep_interval

        filled_data.append(current_row)
        last_row = current_row

    # Continue filling until final_timestep
    if final_timestep is not None:
        while current_timestep <= final_timestep:
            filled_data.append([current_timestep] + last_row[1:])
            current_timestep += timestep_interval

    return filled_data


def main(FPS, DPI, FILE_NAME):
    # Load data
    data, sim_params = load_data("SIM_DATA/SIM_PARAMS/deleted_particle_coords.npy",
                                 "SIM_DATA/SIM_PARAMS/sim_parameters.npy")

    # Unpacking Simulation Parameters
    X_RANGE, Y_RANGE, SPACING, R_OBSTACLE, R_BALLS, TOTAL_NUMBER_OF_BALLS, x_max, x_min, SAVE_PERIOD, final_timestep = sim_params
    data = data[:, 0:2]  # Use only the first two columns

    # Apply the functions to process the data
    combined_data = combine_coordinates(data)
    accumulated_array = accumulate_data(combined_data)
    filled_data = fill_missing_timesteps(accumulated_array, SAVE_PERIOD, -2 * np.abs(x_min), final_timestep)

    # Histogram parameters
    bin_edges = np.linspace(x_min, x_max, int(X_RANGE) + 1)
    max_bin_count = max(np.histogram(row[1:], bins=bin_edges)[0].max() for row in filled_data)

    def update_hist(num, data):
        plt.cla()

        values = data[num][1:]
        hist, bins, _ = plt.hist(values, bins=bin_edges)

        bin_centers = 0.5 * (bins[1:] + bins[:-1])
        plt.xticks(ticks=bin_centers, labels=range(len(bin_centers)), color='white')
        plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))

        plt.xlim(x_min, x_max)
        plt.ylim(0, max_bin_count)

        plt.grid(True, which='both', axis='both', linestyle=':', linewidth=0.5, color='white')

        # Set axes face color and spine color
        ax.set_facecolor('black')
        for spine in ax.spines.values():
            spine.set_color('white')

    # Set up figure and animation
    fig, ax = plt.subplots()
    ani = animation.FuncAnimation(fig, update_hist, frames=len(filled_data), fargs=(filled_data,), interval=1000 / FPS,
                                  repeat=False)

    # Configure figure appearance
    fig.patch.set_facecolor('black')
    ax.set_facecolor('black')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    fig.set_size_inches(1920 / DPI, 1080 / DPI)

    # Change tick and label colors to white
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.tick_params(axis='x', labelsize=40)
    ax.tick_params(axis='y', labelsize=40)

    # Configure and save animation
    writer = FFMpegWriter(fps=FPS, bitrate=15350)
    ani.save(FILE_NAME, writer=writer, dpi=DPI)


if __name__ == "__main__":
    FPS_ = 60
    DPI_ = 100
    FILE_NAME_ = "down_video.mp4"

    main(FPS_, DPI_, FILE_NAME_)
