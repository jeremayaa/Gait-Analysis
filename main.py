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
    'Left_Leg': ('Pelvis', 'Left Upper Leg', 'Left Lower Leg', 'Left Foot', 'Left Toe'),
    'Right_Leg': ('Pelvis', 'Right Upper Leg', 'Right Lower Leg', 'Right Foot', 'Right Toe'),
    'Left_Arm': ('Left Shoulder', 'Left Upper Arm', 'Left Forearm', 'Left Hand'),
    'Right_Arm': ('Right Shoulder', 'Right Upper Arm', 'Right Forearm', 'Right Hand')
    }

class Actor:
    def __init__(self, df, axis=('x', 'z'), reference='Pelvis'):
        data = {}
        for segment in df.columns[:]:
            data[segment] = df[segment][1:].to_numpy()
        self.data = data
        self.coordinates = self.fill_blueprint(axis, reference)
    
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
    

    def get_trace(self, limb_part, blueprint=human_blueprint):
        traces = {}
        limb_part_found = False
        
        for key in blueprint.keys():
            index = 0
            for i in blueprint[key]:
                if i == limb_part:
                    x = np.transpose(self.coordinates[key][0])[index]
                    y = np.transpose(self.coordinates[key][1])[index]
                    limb_part_found = True
                    break
                else:
                    index += 1
        
        traces[limb_part] = (x, y)

        if limb_part_found:
            return traces
        else:
            raise ValueError(f"Limb part '{limb_part}' not found in the blueprint")

Human = Actor(df)
traces = Human.get_trace('Right Toe')

fig, ax = plt.subplots(figsize=(5, 5))
ax.set_aspect('equal')
ax.grid()
ax.set_xlim(-1, 1)
ax.set_ylim(-1, 1)

body = {}
for key in Human.coordinates.keys():
    body[key], = ax.plot([], [], 'o-', lw=2)
    print(key)

body_traces = {}
for key in traces.keys():
    body_traces[key], = ax.plot([], [], '-', lw=1)



def animate(i):
    for key in body.keys():
        # if key=='Trace':
        #     body[key].set_data(Human.coordinates[f'{key}'][0][:i], Human.coordinates[f'{key}'][1][i])
        #     body[key].set_color('red')
        # else:
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
