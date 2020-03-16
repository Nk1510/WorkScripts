import os
import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.signal as signal
import skvideo.io
from scipy.ndimage import gaussian_filter
from scipy.signal import savgol_filter
#sys.path.append('/mnt/data/recherches/code/projects/olftac_naive_2p')



sys.path.append(r'C:\Program Files\WhiskerTracking\python')

from python import traj


def load_measurements(measure_file):
    """Load measurements, such as curvature.

    The data is taken from traj.MeasurementsTable
    I had to guess at what the columns mean, based on example code in
    features() in python/summary.py

    The ordering of the result does not seem to match the ordering derived
    from *.whiskers. I suspect too-small whiskers are being moved after good
    whiskers. You must use 'frame' and 'wid' to line up with other data.
    For this reason I set the index to be 'frame' and 'wid' in this function.

    0 - "smask"? I think this may be a mask that is applied to filter out
        whiskers that are too small. This seems to affect the ordering of
        the results as well (good whiskers moved before bad).
    1 - frame
    2 - wid
    3 - path_length
    4 - median_score
    5 - the "root angle", I think the angle of a few samples around follicle
    6 - curvature
    7, 8 - follicle x and y
    9, 10 - tip x and y

    measure_file : string
        Path to *.measurements file from measure

    convert_to_int : if True, then convert 'frame' and 'wid' columns to int
    set_index : if True, then set index to ['frame', 'wid']
        Don't do this if you want to maintain the ordering of the columns

    Returns: DataFrame
        Has one row for each whisker segment.
        Columns: smask, frame, wid, path_length, score,
            angle, curv, fol_x, fol_y, tip_x, tip_y
        Then ['frame', 'wid'] are set to be the index (see above)
    """

    # Measurements filename cannot be unicode, for some reason
    tmt = traj.MeasurementsTable(str(measure_file))
    tmt_arr = tmt.asarray()
    tmtdf = pd.DataFrame(tmt_arr,
        columns=['smask', 'frame', 'wid', 'path_length', 'score',
            'angle', 'k', 'fol_x', 'fol_y', 'tip_x', 'tip_y'])

    # Convert to float32.
    tmtdf = tmtdf.astype(np.float32)

    # Convert index to int32.
    for col in ['frame', 'wid']:
        tmtdf[col] = tmtdf[col].astype(np.int32)

    # Make index.
    tmtdf = tmtdf.set_index(['frame', 'wid'],
                            verify_integrity=True).sort_index()

    return tmtdf

# Load measurements and save df in preprocessed folder for each recording.
# ------------------------------------------------------------------------

folder = io.videos_a4
exps = (io.S1_fullpad
       + io.S2_fullpad
       + io.peri_sal_fullpad_S1
       + io.peri_cno_fullpad_S1)

for iexp in exps:

    print('Processing {}.'.format(iexp))

    path = os.path.join(folder, iexp)
    files = [f for f in os.listdir(path) if '.measurements' in f]
    files = sorted(files)
    files = [os.path.join(path,f) for f in files]

    dfs = []

    for ifile in files:

        whisk = load_measurements(ifile)

        # Threshold out small curves.
        whisk = whisk.loc[whisk['path_length'] > 150]

        # Keep angle and curvature only.
        whisk = whisk[['angle', 'k']]

        # Add trial index.
        itrial = files.index(ifile)
        whisk['trial'] = itrial

        dfs.append(whisk)

    whisk = pd.concat(dfs)

    # Average angle and curvature along detected whiskers.
    # I take the max for curvature.
    whisk.reset_index(['wid'], drop=True, inplace=True)
    angle = whisk.groupby(['trial','frame'])['angle'].agg('mean')
    k = whisk.groupby(['trial','frame'])['k'].agg('max')
    whisk = pd.DataFrame({'angle': angle, 'k': k})
    whisk = whisk.astype({'angle': np.float32, 'k': np.float32})

    # Add time.
    whisk.reset_index(inplace=True)
    nframes = whisk['frame'].drop_duplicates().shape[0]
    dt = .002
    whisk['time'] = whisk['frame'] * dt
    whisk.drop('frame', axis=1, inplace=True)

    # Compute dkk (substract baseline curvature).
    # Doing it with transform rather than apply would be easier to assign back
    # in df.
    whisk.set_index(['trial','time'])
    f = lambda x: x['k'] - x.loc[x['time']<1]['k'].mean()
    whisk['dkk'] = whisk.groupby(['trial']).apply(f).reset_index(['trial'], drop=True)
    whisk.drop('k', axis=1, inplace=True)

    # Add condition column.
    seq_path = os.path.join(io.data_a3, iexp, iexp + '_sequence_correct.bin')
    seq = np.fromfile(seq_path, dtype='int8')
    whisk['cond'] = (whisk[['trial']].applymap(lambda x: seq[x]))

    # Add exp_id.
    whisk['exp_id'] = io.exps_id[iexp]

    # Optimize types.
    whisk = whisk.astype({'exp_id':np.uint16, 'trial':np.uint16, 'cond':np.uint8, 'time':np.float32})
    # Save df in preprocessed folder.
    save_path = os.path.join(io.preprocessed_a3, iexp)
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    save_path = os.path.join(save_path, iexp + '_whisk.h5')
    with pd.HDFStore(save_path) as store:
        store.put('whisk', whisk, format='table')
