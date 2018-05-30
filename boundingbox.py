import numpy as np
from read import read_main_df

df = read_main_df()

#load users and stimuli names from the dataframe
users = df.user.unique()
stimuli_names = df.StimuliName.unique()



#dictionary to store x/y max/min values
bounding = {}
#dictionary to store similarity scores
adjacency = {}

#fill in this dictionary for each stimuli and user
for stim in stimuli_names:
    bounding[stim] = {} #create a new dictionray with the stimuli as key
    adjacency[stim] = {} #same for the matrix that stores similarity scores
    for user in users:
        adjacency[stim][user] = {}
        temp = df[(df['StimuliName'] == stim) & (df['user'] == user)] #create small temporary dataset containing the entire scanpath of an user
        bounding[stim][user] = {'x_max' : temp['MappedFixationPointX'].max(),
                                'y_max' : temp['MappedFixationPointY'].max(),
                                'x_min': temp['MappedFixationPointX'].min(),
                                'y_min': temp['MappedFixationPointY'].min(),}

#dictionary struture: {'paris.jpg' : {'p1' : {'x_max' : 10, 'y_max' : 10, 'x_min' : 0, 'y_min' : 0}, p2 : {'x_max' : 10, 'y_max' : 10, 'x_min' : 0, 'y_min' : 0} ...etc

#compute overlap values
for stim in bounding:
    counter = 0 #
    for i in users:
        for j in users[counter:len(users)]:
            if np.isnan(bounding[stim][i]['x_max']) or np.isnan(bounding[stim][j]['x_max']):
                continue
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

#dictionary struture: {'paris.jpg' : {'p1' : {'p1' : 1.0, 'p4' : 0.399, 'p5' : 0.85 ...etc} 'p2' : { 'p2' : 1.0 ...etc}}



