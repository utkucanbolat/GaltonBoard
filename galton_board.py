import os
import numpy as np

# system parameters
TOTAL_NUMBER_OF_BALLS = 1000  # total number of balls
X_RANGE, Y_RANGE = 15, 10  # number of fixed balls along x and y directions
SPACING = 1  # distance between two fixed balls
R_OBSTACLE = 0.25  # radii of the fixed balls
R_BALLS = 0.1  # radii of the moving balls
DELETED_PARTICLE_COORS = []  # keep the coordinates of the balls passed the deletion boundary in this list
SAVE_PERIOD = 10000
DATA_SAVE_DIR = "SIM_DATA"

stl_save_path = os.path.join(DATA_SAVE_DIR, "STL_DATA")
os.makedirs(stl_save_path, exist_ok=True)
sim_params_path = os.path.join(DATA_SAVE_DIR, "SIM_PARAMS")
os.makedirs(sim_params_path, exist_ok=True)

# make the grid
for y in range(Y_RANGE):
    for x in range(X_RANGE - (y % 2)):
        O.bodies.append([sphere(center=(x + (SPACING / 2) * (y % 2), -y, 0), radius=R_OBSTACLE, fixed=True)])

# add walls to right and left boundaries
x_min, x_max = aabbExtrema()[0][0], aabbExtrema()[1][0]
w_left = utils.wall(x_min, axis=0)
w_right = utils.wall(x_max, axis=0)
O.bodies.append([w_left, w_right])

# add balls
ball_counter = 0


def create_particle():
    global ball_counter, TOTAL_NUMBER_OF_BALLS

    if ball_counter < TOTAL_NUMBER_OF_BALLS:
        O.bodies.append(
            sphere(center=(
            np.random.uniform(low=(x_max + x_min) / 2 - SPACING / 4, high=(x_max + x_min) / 2 + SPACING / 4), SPACING,
            0),
                   radius=R_BALLS))
        O.bodies[-1].state.blockedDOFs = "zXY"
        ball_counter += 1
    else:
        stop_simulation()


# delete the particles if their y-coor exceeds a certain level
def deletion_boundary():
    global DELETED_PARTICLE_COORS

    for b in O.bodies:
        if b.state.pos[1] < - Y_RANGE * SPACING + SPACING / 2:
            DELETED_PARTICLE_COORS.append(np.append(int(O.iter), np.array(b.state.pos)))
            O.bodies.erase(b.id)


# stop simulation after every particle gets deleted
def stop_simulation():
    if ball_counter == len(DELETED_PARTICLE_COORS):
        O.pause()
        dump_deleted_particle_coors()


# dump coordinates with respect to iteration in order to plot the coordinates after
def dump_deleted_particle_coors():
    np.save(f"{os.path.join(sim_params_path, 'deleted_particle_coords.npy')}", np.array(DELETED_PARTICLE_COORS))
    np.save(f"{os.path.join(sim_params_path, 'sim_parameters.npy')}", np.array(
        [X_RANGE, Y_RANGE, SPACING, R_OBSTACLE, R_BALLS, TOTAL_NUMBER_OF_BALLS, x_max, x_min, SAVE_PERIOD,
         O.iter]))  # I know this is ugly, but it does its job.


# define engine, use default values
O.engines = [
    ForceResetter(),
    InsertionSortCollider([Bo1_Sphere_Aabb(), Bo1_Wall_Aabb()]),
    InteractionLoop(
        [Ig2_Sphere_Sphere_ScGeom(), Ig2_Wall_Sphere_ScGeom()],
        [Ip2_FrictMat_FrictMat_FrictPhys()],
        [Law2_ScGeom_FrictPhys_CundallStrack()]
    ),

    NewtonIntegrator(gravity=(0, -9.81, 0), damping=0.3),
    PyRunner(command="create_particle()", iterPeriod=50000),
    PyRunner(command="deletion_boundary()", iterPeriod=SAVE_PERIOD),
    VTKRecorder(fileName=f"{stl_save_path}/galton_", recorders=["spheres"], iterPeriod=SAVE_PERIOD),
]

# timestep
O.dt = 1e-5
