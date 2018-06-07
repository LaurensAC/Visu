from utils import find_path, convert_type, read_sv, track
import json
import pandas as pd

# Use this module to read data from disk


def read_main_df():
    # Reading main data into memory
    df = read_sv(return_as=pd.DataFrame,
                 path=find_path('up.csv'),
                 encoding='utf-8',
                 delimiter='\t',
                 header=True)

    assert 'FixationOOB' in df.columns
    # Mapping FixationOOB strings to numpy booleans
    OOBstatus = {'True': True, 'False': False, 'Edge': False}
    df['FixationOOB'].map(OOBstatus)

    convert_type(df,
                 Timestamp='int64', FixationDuration='int64',
                 MappedFixationPointX='int64', MappedFixationPointY='int64',
                 StimuliName='str')

    print('Read df as pd.DataFrame')

    return df


def read_metadata():
    print('Found metadata at {}'.format(find_path('meta.json')))
    with open(find_path('stimuli_meta.json'), 'r') as f:
        stimuli_meta = json.load(f)
    return stimuli_meta

a = read_main_df()

print(a.dtypes)

for item in a.FixationOOB:
    if item == False:
        print(item)
    else:
        print(item)