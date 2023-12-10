import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def extract_dataframe(set, type, terrain='Treadmill', sheet='Segment Position'):
    path = 'data/set{}/{}_Gait_{}.xlsx'.format(set, type, terrain)
    return pd.read_excel(path, sheet_name=sheet)

df = extract_dataframe(set=4, type='Normal', terrain='Treadmill', sheet='Segment Position')

human_blueprint = {
    'Spine': ('Pelvis', 'Neck', 'Head'),
    'Left Leg': ('Pelvis', 'Left Upper Leg', 'Left Lower Leg', 'Left Foot', 'Left Toe'),
    'Right Leg': ('Pelvis', 'Right Upper Leg', 'Right Lower Leg', 'Right Foot', 'Right Toe'),
    'Left Arm': ('Neck', 'Left Shoulder', 'Left Upper Arm', 'Left Forearm', 'Left Hand'),
    'Right Arm': ('Neck', 'Right Shoulder', 'Right Upper Arm', 'Right Forearm', 'Right Hand')
    }


class Actor:
    def __init__(self, df):
        data = {}
        for segment in df.columns[:]:
            data[segment] = df[segment][1:].to_numpy()
        self.data = data
    
    def fill_blueprint(self, axis=('y', 'z'), reference='Pelvis'):
        """
        The 'coordinates' dictionary associates two values (one for 'x' and one for 'y' coordinates) 
        with each key representing a limb. 
        Each value is a 2D array, where each row corresponds to 'x' or 'y' coordinates 
        for the respective limb part at a given time.
        """
    
        coordinates = {}

        for limb, limb_tuple in human_blueprint.items():
            limb_coordinates_x = np.transpose(
                np.array([self.data['{} {}'.format(limb_part, axis[0])] - self.data['{} {}'.format(reference, axis[0])]
                          for limb_part in limb_tuple])
            )

            limb_coordinates_y = np.transpose(
                np.array([self.data['{} {}'.format(limb_part, axis[1])] - self.data['{} {}'.format(reference, axis[1])]
                          for limb_part in limb_tuple])
            )

            coordinates[limb] = (limb_coordinates_x, limb_coordinates_y)

        return coordinates

Human = Actor(df)
cords = Human.fill_blueprint(axis=('x', 'z'))

fig, ax = plt.subplots(figsize=(5, 5))
ax.set_aspect('equal')
ax.grid()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)


R_leg, = ax.plot([], [], 'o-', lw=2)
L_leg, = ax.plot([], [], 'o-', lw=2)
R_arm, = ax.plot([], [], 'o-', lw=2)
L_arm, = ax.plot([], [], 'o-', lw=2)
Spine, = ax.plot([], [], 'o-', lw=2)

trace_len = 1000

def animate(i):
    
    L_leg.set_data(cords['Left Leg'][0][i], cords['Left Leg'][1][i])
    R_leg.set_data(cords['Right Leg'][0][i], cords['Right Leg'][1][i])
    L_arm.set_data(cords['Left Arm'][0][i], cords['Left Arm'][1][i])
    R_arm.set_data(cords['Right Arm'][0][i], cords['Right Arm'][1][i])
    Spine.set_data(cords['Spine'][0][i], cords['Spine'][1][i])
    
    R_leg.set_color('blue')
    L_leg.set_color('blue')
    R_arm.set_color('blue')
    L_arm.set_color('blue')
    Spine.set_color('blue')
    
    return L_leg, R_leg, L_arm, R_arm, Spine,

length = 2000
ani = animation.FuncAnimation(
    fig, animate, length, interval=20, blit=True)
plt.show()

