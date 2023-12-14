import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import warnings

def extract_dataframe(set, type, terrain='Treadmill', sheet='Segment Position'):
    path = 'data/set{}/{}_Gait_{}.xlsx'.format(set, type, terrain)
    return pd.read_excel(path, sheet_name=sheet)

df = extract_dataframe(set=5, type='Normal', terrain='Treadmill', sheet='Segment Position')

human_blueprint = {
    'Spine': ('Pelvis', 'Neck', 'Head'),
    'Left_Leg': ('Pelvis', 'Left Upper Leg', 'Left Lower Leg', 'Left Foot', 'Left Toe'),
    'Right_Leg': ('Pelvis', 'Right Upper Leg', 'Right Lower Leg', 'Right Foot', 'Right Toe'),
    'Left_Arm': ('Left Shoulder', 'Left Upper Arm', 'Left Forearm', 'Left Hand'),
    'Right_Arm': ('Right Shoulder', 'Right Upper Arm', 'Right Forearm', 'Right Hand')
    }

legs_blueprint = {
    'Left_Leg': ('Pelvis', 'Left Upper Leg', 'Left Lower Leg', 'Left Foot', 'Left Toe'),
    'Right_Leg': ('Pelvis', 'Right Upper Leg', 'Right Lower Leg', 'Right Foot', 'Right Toe'),
}


class Actor:
    def __init__(self, df, axis=('x', 'z'), reference='Pelvis', blueprint=human_blueprint):
        data = {}
        for segment in df.columns[:]:
            data[segment] = df[segment][1:].to_numpy()
        self.data = data
        self.blueprint=blueprint
        self.coordinates = self.fill_blueprint(axis, reference)
    
    def fill_blueprint(self, axis, reference):

        """
        The 'coordinates' dictionary associates two values (one for 'x' and one for 'y' coordinates) 
        with each key representing a limb. 
        Each value is a 2D array, where each row corresponds to 'x' or 'y' coordinates 
        for the respective limb part at a given time.

        Reverence is the body part that stays at coordinates (0, 0). Every other part is relative to it.
        """
    
        coordinates = {}

        for limb, limb_tuple in self.blueprint.items():
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
    

    def get_trace(self, *limb_part):
        traces = {}
        parts_found = 0
        
        for key in self.blueprint.keys():
            index = 0
            for i in self.blueprint[key]:
                if i in limb_part:
                    x = np.transpose(self.coordinates[key][0])[index]
                    y = np.transpose(self.coordinates[key][1])[index]
                    traces[i] = (x, y)
                    parts_found+=1
                else:
                    index += 1        

        if parts_found<len(limb_part):
            warnings.warn("Not all limbs part are found and tracked. Check for spelling mistakes in 'get_trace' arguments")
        if parts_found>0:
            return traces
        else:
            raise ValueError(f"Limb part '{limb_part}' not found in the blueprint")

Human = Actor(df, blueprint=human_blueprint)
traces = Human.get_trace('Right Toe', 'Left Hand')

fig, ax = plt.subplots(figsize=(5, 5))
ax.set_aspect('equal')
ax.grid()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

body = {}
for key in Human.coordinates.keys():
    body[key], = ax.plot([], [], 'o-', lw=2)

body_traces = {}
for key in traces.keys():
    body_traces[key], = ax.plot([], [], '-', lw=1)

def animate(i):
    for key in body.keys():
        body[key].set_data(Human.coordinates[f'{key}'][0][i], Human.coordinates[f'{key}'][1][i])
        body[key].set_color('blue')

    for key in traces.keys():
        body_traces[key].set_data(traces[f'{key}'][0][:i], traces[f'{key}'][1][:i])
        body_traces[key].set_color('red')

    return (*body.values(), *body_traces.values(),) 

length = 2000
ani = animation.FuncAnimation(
    fig, animate, length, interval=20, blit=True)
plt.show()
