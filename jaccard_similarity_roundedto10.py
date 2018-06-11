import numpy as np
import math

rounded = df.copy()

def jaccard_similarity(stim, users, rounded):
    
    #make function to round X and Y coordinates, rounded to 10 right now
    def roundup(x):
        return int(math.ceil(x / 10.0)) * 10     

    rounded['MappedFixationPointX'] = rounded['MappedFixationPointX'].apply(roundup)
    rounded['MappedFixationPointY'] = rounded['MappedFixationPointY'].apply(roundup)
    
    #load users and stimuli names from the dataframe
    users = rounded.user.unique()
    stimuli_names = rounded.StimuliName.unique()
    
    #dictionary to store x/y max/min values
    jaccard[stim] = {}
    #dictionary to store similarity scores
    adjacency[stim] = {}
    
    #fill in this dictionary for each stimuli and user
    for user in users:
            adjacency[user] = {}
            list_X = list(rounded['MappedFixationPointX'][rounded['user'] == user][rounded['StimuliName'] == stim ])
            list_Y = list(rounded['MappedFixationPointY'][rounded['user'] == user][rounded['StimuliName'] == stim ])
            zipped = list(zip(list_X,list_Y)) #make tuples of corresponding X and Y coordinate
            jaccard[stim][user] = zipped
    #dictionary struture: {'paris.jpg' : {'p1' : {(1151, 458),(1371, 316),(1342, 287),(762, 303)]}, p2 : {[(670, 450),(1355, 249),(511, 791)]} ...etc
    
    
    Unique = {}# dictionary to store unique users per Stimuli
    for stim in jaccard:
        Unique[stim] = rounded[rounded['StimuliName'] == stim].user.unique()
        
    #compute jaccard similarity
    counter = 0
    for i in Unique[stim]:
        for j in Unique[stim][counter:len(Unique[stim])]:
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
        
    return adjacency
