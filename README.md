# Galton Board Simulation with YADE

## Overview
This repository contains a Discrete Element Method (DEM) simulation of the Galton Board system, utilizing the open-source DEM software, YADE. It is comprised of two main components:

- `galton_board.py`: Runs the simulation.
- `plotter.py`: Processes the simulation output and visualizes the results.

## Getting Started

### Prerequisites
Ensure you have YADE installed on your system. For installation instructions, refer to the [YADE documentation](https://yade-dem.org/doc/).

### Running the Simulation

1. **Simulation Script**: 
    To start the simulation, open your terminal and run the following command:
    ```
    yade galton_board.py
    ```
    or for yadedaily builds:
    ```
    yadedaily galton_board.py
    ```

    This function creates a `SIM_DATA` folder, generates STL files, and records the corresponding simulation parameters.

2. **Data Visualization**:
    After running the simulation, use `plotter.py` to process the STL files and simulation parameters. This script plots a histogram for each timestep and combines these plots to create a video. Run the following command in your terminal:
    ```
    python plotter.py
    ```

---

For any queries or issues, feel free to open an issue or contact the repository maintainers.
