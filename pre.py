from utils import *

path = find_path('up.csv')

# encoding = find_encoding(path)
# returns ISO-8859-1

encoding = 'ISO-8859-1'

a = read_sv(return_as=pd.DataFrame,
            path=path,
            encoding=encoding,
            delimiter='\t',
            header=True)

print(a.shape)
print(a.size)
print(a.memory_usage(index=False, deep=True))

a = read_sv(return_as=list,
            path=path,
            encoding=encoding,
            delimiter='\t',
            header=True)


import sys

print(sys.getsizeof(a))
bytes = 0
for element in a:
    bytes += sys.getsizeof(element)
print(bytes)

