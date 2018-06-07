import math
import subprocess
import os
import csv
import pandas as pd
# import Levenshtein
from chardet.universaldetector import UniversalDetector
from functools import wraps
from time import time
import numpy as np
import scipy
import pylab
import scipy.cluster.hierarchy as sch


# Wrap a function with @track to check execution time
def track(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print('function:{} \n\t args:[{}] \n\t took {} seconds'
              .format(f.__name__, args, round(te-ts, 4)))
        return result
    return wrap


def find_path(end_of_file=str()):
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(end_of_file):
                return os.path.join(root, file)


def find_encoding(path_to_file):
    # 'rb' to stream bytestrings (we don't know the encoding yet)
    file = open(path_to_file, 'rb')
    detector = UniversalDetector()
    # Do not feed all the lines if file is big
    for line in file.readlines():
        detector.feed(line)
        #if detector.done: break
    detector.close()
    file.close()

    print(detector.result)
    return detector.result['encoding']


def read_sv(return_as, path,
            encoding=str(),
            delimiter=str(),
            header=bool()):

    with open(path, 'r', encoding=encoding) as f:
        reader = csv.reader(f, delimiter=delimiter)
        rows = list()
        if header:
            colnames = next(reader)
        else:
            colnames = None
        for row in reader:
            rows.append(row)

        if isinstance(return_as(), pd.DataFrame):
            return return_as(rows, columns=colnames)
        elif isinstance(return_as(), list):
            return [colnames] + rows

    return colnames, rows


def convert_type(df, **kwargs):
    """
    Modifies (!) a DataFrame
    :param df: pandas DataFrame
    :param kwargs: column names and the types their values should be cast in
    """
    for column, dtype in kwargs.items():
        df[column] = df[column].astype(dtype, errors='raise')


def levenshtein(source, target):
    """
    Informally, the Levenshtein distance between two words is the minimum
    number of single-character edits (insertions, deletions or substitutions)
    required to change one word into the other. -Wikipedia

    :returns Amount of edits required to change source into target
    """
    # return Levenshtein.distance(source, target)
    pass

def lowest_levenshtein(source, target_list):
    """
    :return Target with lowest levenshtein distance w.r.t. source
    """
    assert type(target_list) == list

    min_distance = math.inf
    matched_target = str()

    for target in target_list:
        similarity = levenshtein(source, target)
        if similarity < min_distance:
            min_distance = similarity
            matched_target = target

    return matched_target


def capture_str_subp(command):
    """
    Capturing subprocess output as string
    :param command: shell command to be executed
    :return: decoded output of shell
    """
    subp = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return subp.stdout.decode('utf-8')


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



