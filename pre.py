from utils import *
import re

### --- GROUP ASSIGNMENT WEEK 1 / 2 --- ###

# Path to csv
path = find_path('up.csv')
# find_encoding(path) returns ISO-8859-1
encoding = 'ISO-8859-1'

# Reading main data into memory
df = read_sv(return_as=pd.DataFrame,
             path=path,
             encoding=encoding,
             delimiter='\t',
             header=True)

# Casting columns to appropriate type
convert_type(df,
             Timestamp='int64', FixationDuration='int64',
             MappedFixationPointX='int64', MappedFixationPointY='int64',
             StimuliName='str')

# Making a lookup table for stimuli names and e.g. their resolutions
stimuli_meta = dict()
# The different maps
for stimuli in df.StimuliName.unique():
    # Keys are 'StimuliName' values
    stimuli_meta[stimuli] = dict()

# --- Adding clean city names e.g. "19b_New_York_S2.jpg" becomes "New_York"
for stimuli, values in stimuli_meta.items():
    # Capturing what is between first and last underscore
    city_name = stimuli.rsplit('_', 1)[0].split('_', 1)[-1]
    # Adding the new variable to look up in later stage
    values.update({'csv_name': city_name})

# --- Adding resolutions

# Reading resolutions into memory as DataFrame
resolutions = pd.read_excel(find_path('xlsx'), header=None,
                            names=['city', 'x', 'y']).dropna()  # Dropping NaNs

# Matching names from xlsx file with main file names using Levenshtein distance
for stimuli, values in stimuli_meta.items():
    xslx_name = lowest_levenshtein(values['csv_name'], list(resolutions.city))

    x_dim = resolutions.loc[resolutions['city'] == xslx_name]['x'].values[0]
    y_dim = resolutions.loc[resolutions['city'] == xslx_name]['y'].values[0]

    values.update({'xlsx_name': xslx_name,
                   'x_dim': x_dim,
                   'y_dim': y_dim})

# --- Adding station count ("complexity")

# Reading as string
stations = open(find_path('complexity.txt'), 'r').read()
# Listing station names
txt_names = re.findall(r'(\w+\s*\w+\s*(?=\(\d+\)))', stations)
# Listing station counts
count_matches = re.findall(r'(\(\d+\))', stations)

# Removing brackets from the matches, changing type to int
counts = [int(x.replace(')', '').replace('(', '')) for x in count_matches]
# Joining names with counts in a dict, names as keys
assert len(counts) == len(txt_names)
parsed_stations = dict(zip(txt_names, counts))

# Adding to lookup table
for stimuli, values in stimuli_meta.items():
    # Matching station name with stimuli name
    txt_name = lowest_levenshtein(values['csv_name'], txt_names)
    # Add to lookup together with number of stations
    values.update({'txt_name': txt_name,
                   'station_count': parsed_stations[txt_name]})

# Skrrrrpopop
# print(stimuli_meta.popitem())


# add Fixation point out of bounds column
df['FixationOOB'] = pd.Series(data=None, index=df.index, dtype=bool)


# search resolution and return true if fixation point is out of bounds
def compareResolution(x, y, stim):
    if x > stimuli_meta.get(stim).get('x_dim') or x < 0 \
            or y > stimuli_meta.get(stim).get('y_dim') or y < 0:
        return True
    return False


# iterate trough each fixation point
for index, row in df.iterrows():
    # Comparing resolutions and adding result to main dataframe
    df.FixationOOB.at[index] = compareResolution(row['MappedFixationPointX'],
                                                 row['MappedFixationPointY'],
                                                 row['StimuliName'])

# total amount of fixation points outside of bounds
print(df['FixationOOB'].sum())
# percentage outside of bounds
print(df['FixationOOB'].sum() / 118126)

# Assignment Week 1
"""
print(df.shape)
print(df.size)
print(df.memory_usage(index=False, deep=True))
df = read_sv(return_as=list,
            path=path,
            encoding=encoding,
            delimiter='\t',
            header=True)
import sys
print(sys.getsizeof(df))
bytes = 0
for element in df:
    bytes += sys.getsizeof(element)
print(bytes)
"""
