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

    for i, row in df.iterrows():
            df.at[i, 'FixationOOB'] = eval(df.at[i, 'FixationOOB'])

    convert_type(df,
                 Timestamp='int64', FixationDuration='int64',
                 MappedFixationPointX='int64', MappedFixationPointY='int64',
                 StimuliName='str', FixationOOB='?')

    print('Read df as pd.DataFrame')

    return df


def read_metadata():
    if not find_path('stimuli_meta.json'):
        raise FileNotFoundError
    else:  # Read from disk otherwise
        print('Found metadata at {}'.format(find_path('meta.json')))
        with open(find_path('stimuli_meta.json'), 'r') as f:
            stimuli_meta = json.load(f)

    return stimuli_meta
