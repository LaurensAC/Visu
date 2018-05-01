import csv
import os
import pandas as pd
from chardet.universaldetector import UniversalDetector


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
