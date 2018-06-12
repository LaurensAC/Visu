import numpy as np
from read import read_main_df

df = read_main_df()
stimuli_names = df.StimuliName.unique()

def scanpaths_dict(stim, users, df):
    # dictionary to store x/y max/min values
    bounding = {}
    # dictionary to store similarity scores
    adjacency = {}

    bounding[stim] = {}
    adjacency[stim] = {}

    for user in users:
        adjacency[stim][user] = {}
        temp = df[(df['StimuliName'] == stim) & (df[
                                                     'user'] == user)]  # create small temporary dataset containing the entire scanpath of an user
        bounding[stim][user] = {'x_max': temp['MappedFixationPointX'].max(),
                                'y_max': temp['MappedFixationPointY'].max(),
                                'x_min': temp['MappedFixationPointX'].min(),
                                'y_min': temp['MappedFixationPointY'].min(), }

    counter = 0 #
    for i in users:
        for j in users[counter:len(users)]:
            #if np.isnan(bounding[stim][i]['x_max']) or np.isnan(bounding[
            # stim][j]['x_max']):
            #    print(bounding[stim][user], user)
            #    continue
            A = abs(bounding[stim][i]['x_max'] - bounding[stim][i]['x_min']) *\
                abs(bounding[stim][i]['y_max'] - bounding[stim][i]['y_min'])
            B = abs(bounding[stim][j]['x_max'] - bounding[stim][j]['x_min']) *\
                abs(bounding[stim][j]['y_max'] - bounding[stim][j]['y_min'])

            C = abs(max(bounding[stim][i]['x_min'], bounding[stim][j]['x_min']) -\
                    min(bounding[stim][i]['x_max'], bounding[stim][j]['x_max'])) *\
                abs(max(bounding[stim][i]['y_min'], bounding[stim][j]['y_min']) - \
                    min(bounding[stim][i]['y_max'], bounding[stim][j]['y_max']))

            #fill in the matrix
            adjacency[stim][i][j] = C / (A + B - C)
            adjacency[stim][j][i] = C / (A + B - C)
        counter += 1
    print(adjacency)
    return adjacency
