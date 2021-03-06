import math
import subprocess
import os
import types
from functools import wraps
from time import time
import csv
import pandas as pd
import numpy as np
from bokeh.models.renderers import GlyphRenderer
from chardet.universaldetector import UniversalDetector


def get_functions_dict(module):
    # Returns a {function_name: function, ...} mapping given a module
    funcs = dict()
    for func in dir(module):
        if isinstance(module.__dict__.get(func), types.FunctionType):
            funcs[func] = module.__dict__.get(func)
    return funcs


# Wrap a function with @track to check and print execution time
def track(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print('function:{} \n\t args:[{}] \n\t took {} seconds \n'
              .format(f.__name__, args, round(te - ts, 4)))
        return result

    return wrap


# The above without printing input arguments
def strack(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        ts = time()
        result = f(*args, **kwargs)
        te = time()
        print('function: {} \n\t took {} seconds \n'
              .format(f.__name__, round(te-ts, 4)))

        return result
    return wrap


def find_path(end_of_file=str()):
    for root, dirs, files in os.walk(os.getcwd()):
        for file in files:
            if file.endswith(end_of_file):
                return os.path.join(root, file)
    raise FileNotFoundError


def find_encoding(path_to_file):
    # 'rb' to stream bytestrings (we don't know the encoding yet)
    file = open(path_to_file, 'rb')
    detector = UniversalDetector()
    # Do not feed all the lines if file is big
    for line in file.readlines():
        detector.feed(line)
        # if detector.done: break
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


def capture_str_subp(command):
    """
    Capturing subprocess output as string
    :param command: shell command to be executed
    :return: decoded output of shell
    """
    subp = subprocess.run(command, shell=True, stdout=subprocess.PIPE)
    return subp.stdout.decode('utf-8')


# DEPRECATED, depends on python-dev, build-essentials and python-levenshtein


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

def remove_glyphs(figure, glyph_name_list):
    renderers = figure.select(dict(type=GlyphRenderer))
    for r in renderers:
        if r.name in glyph_name_list:
            col = r.glyph.y
            r.data_source.data[col] = [np.nan] * len(r.data_source.data[col])