from utils import find_path, convert_type, read_sv, strack
import json
import pandas as pd

# Use this module to read data from disk


@strack
def read_main_df():
    # Reading main data into memory
    df = read_sv(return_as=pd.DataFrame,
                 path=find_path('up.csv'),
                 encoding='utf-8',
                 delimiter='\t',
                 header=True)

    assert 'FixationOOB' in df.columns
    # Mapping FixationOOB strings to numpy booleans
    OOBstatus = {'True': True, 'False': False}
    df['FixationOOB'] = df['FixationOOB'].replace(OOBstatus)

    convert_type(df,
                 Timestamp='int64', FixationDuration='int64',
                 MappedFixationPointX='int64', MappedFixationPointY='int64',
                 StimuliName='object')

    return df


@strack
def read_metadata():
    with open(find_path('stimuli_meta.json'), 'r') as f:
        stimuli_meta = json.load(f)
    return stimuli_meta
