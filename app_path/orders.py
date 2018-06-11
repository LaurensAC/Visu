import numpy as np
import math
import scipy.cluster.hierarchy as sch

# TODO Laurens, Neil:
# Wats met 'column'? (kan het zonder?) (non-deterministisch?)
# >>> zou chill zijn als alle functies dezelfde input krijgen e.g. de matrix

# Geef de functies namen waar de gebruiker ('client') wat aan heeft


#uses squared distance matrix + double centering + SVD
def seriationMDS(matrix, column):
    np.random.seed(0)
    lengte = len(matrix["count"])
    wortellengte = int(math.sqrt(lengte))
    for i in range(0, lengte-1):
        matrix["count"][i] = (1 - matrix["count"][i]) ** 2
    A = np.array(matrix["count"]).reshape((wortellengte, wortellengte))
    names = np.array(matrix["xname"]).reshape((wortellengte, wortellengte))
    names = [row[0] for row in names]
    n = A.shape[0]
    J_c = 1. / n * (np.eye(n) - 1 + (n - 1) * np.eye(n))

    # perform double centering
    B = -0.5 * (J_c.dot(A)).dot(J_c)

    U, E, V = np.linalg.svd(B)
    U = [row[column] for row in U]

    U, names = zip(*sorted(zip(U, names)))
    U, names = (list(t) for t in zip(*sorted(zip(U, names))))
    return names


#only uses SVD
def seriationMDS3(matrix, column):
    np.random.seed(0)
    lengte = len(matrix["count"])
    wortellengte = int(math.sqrt(lengte))

    A = np.array(matrix["count"]).reshape((wortellengte, wortellengte))
    names = np.array(matrix["xname"]).reshape((wortellengte, wortellengte))
    names = [row[0] for row in names]


    U, E, V = np.linalg.svd(A)
    U = [row[column] for row in U]

    U, names = zip(*sorted(zip(U, names)))
    U, names = (list(t) for t in zip(*sorted(zip(U, names))))
    return names

#uses distance matrix + SVD
def seriationMDS5(matrix, column):
    np.random.seed(0)
    lengte = len(matrix["count"])
    wortellengte = int(math.sqrt(lengte))
    for i in range(0, lengte-1):
        matrix["count"][i] = (1 - matrix["count"][i])
    A = np.array(matrix["count"]).reshape((wortellengte, wortellengte))
    names = np.array(matrix["xname"]).reshape((wortellengte, wortellengte))
    names = [row[0] for row in names]


    U, E, V = np.linalg.svd(A)
    U = [row[column] for row in U]

    U, names = zip(*sorted(zip(U, names)))
    U, names = (list(t) for t in zip(*sorted(zip(U, names))))
    return names

#Neil zijn shit
def sorting(d):
    lengte = len(d["count"])
    wortellengte = int(math.sqrt(lengte))

    D2 = np.array(d["count"]).reshape((wortellengte, wortellengte))
    names = np.array(d["xname"]).reshape((wortellengte, wortellengte))
    names = [row[0] for row in names]

    #Y = sch.linkage(D2, method='complete')
    Z = sch.dendrogram(sch.linkage(D2, method='single'),no_plot = True, orientation='right')
    names2 = [None] * len(names)
    for i in range(len(names)):
        names2[i] = names[int(Z['ivl'][i])-1]
    return names2