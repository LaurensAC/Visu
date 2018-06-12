import numpy as np
import math


def simple_bbox(stim, users, df):
    """
    A metric
    """

    # dictionary to store x/y max/min values
    bounding = {}
    # dictionary to store similarity scores
    adjacency = {}

    bounding[stim] = {}
    adjacency[stim] = {}

    for user in users:
        adjacency[stim][user] = {}
        temp = df[(df['StimuliName'] == stim) & (df['user'] == user)]  # create small temporary dataset containing the entire scanpath of an user
        bounding[stim][user] = {'x_max': temp['MappedFixationPointX'].max(),
                                'y_max': temp['MappedFixationPointY'].max(),
                                'x_min': temp['MappedFixationPointX'].min(),
                                'y_min': temp['MappedFixationPointY'].min(), }

    counter = 0
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

    return adjacency



def jaccard_similarity(stim, users, df):

    jaccard = {}  # ?
    adjacency = {}  # ?

    # make function to round X and Y coordinates, rounded to 10 right now
    def roundup(x):
        return int(math.ceil(x / 10.0)) * 10

    df['MappedFixationPointX'] = df['MappedFixationPointX'].apply(
        roundup)
    df['MappedFixationPointY'] = df['MappedFixationPointY'].apply(
        roundup)

    # dictionary to store x/y max/min values
    jaccard[stim] = {}
    # dictionary to store similarity scores
    adjacency[stim] = {}

    for user in users:
        list_X = list(df['MappedFixationPointX'][df['user'] == user][
                          df['StimuliName'] == stim])
        list_Y = list(df['MappedFixationPointY'][df['user'] == user][
                          df['StimuliName'] == stim])
        zipped = list(zip(list_X,
                          list_Y))  # make tuples of corresponding X and Y coordinate
        jaccard[stim][user] = zipped

    # dictionary struture: {'paris.jpg' : {'p1' : {(1151, 458),(1371, 316),(1342, 287),(762, 303)]}, p2 : {[(670, 450),(1355, 249),(511, 791)]} ...etc

    Unique = {}  # dictionary to store unique users per Stimuli

    for stim in jaccard:
        Unique[stim] = df[df['StimuliName'] == stim].user.unique()
        print(Unique[stim])

    # compute jaccard similarity
    counter = 0
    for i in Unique[stim]:
        adjacency[stim][i] = {}  # ?
        for j in Unique[stim][counter:len(Unique[stim])]:
            adjacency[stim][j] = {}  # ?
            listA = [item for list in jaccard[stim][i] for item in list]
            listB = [item for list in jaccard[stim][j] for item in list]
            A = len(set(listA).intersection(listB))
            B = len(set(listA))
            C = len(set(listB))

            if (B | C - A) == 0:
                continue
            adjacency[stim][i][j] = A / (B | C - A)
            adjacency[stim][j][i] = A / (B | C - A)
        counter += 1

    print(adjacency)
    return adjacency
