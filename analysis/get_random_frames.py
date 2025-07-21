import h5py
import numpy as np
import get_xyz
import constants
from pathlib import Path
import hdf5plugin
import add_geometry_streaks
import sys
from tqdm import tqdm

run = int(sys.argv[1])


# find pattern with a lot of streaks
# check that input dir exists
run_dir = Path(f'{constants.raw}/run{run:>04}/data')
assert(run_dir.is_dir())

# get file list
fnams = sorted(list(run_dir.glob('acq*.JF07T32V02.h5')))

fnam = fnams[0]
with h5py.File(fnam) as f:
    data = f['/data/JF07T32V02/data']

    D = data.shape[0]
    for d in tqdm(range(D)):
        a = data[d]

"""
fnam = Path(constants.beamtime_dir) / f'work/streaks/streaks_run{run:>04}.h5'
if fnam.is_file():
    with h5py.File(fnam) as f:
        streaks = f['fs0_ss0_fs1_ss1_slab'][()]
        pid = np.squeeze(f['pulse_id'][()])
        fnams = f['file_name'][()]
        file_index = f['file_index'][()]

    streaks_pid = np.bincount(pid-pid.min())
    j = np.argsort(streaks_pid)[-100:]
    pid_max = (j + pid.min()).astype(int)
    i = [np.where(jj==pid)[0][0] for jj in pid_max]
    fnams_i = fnams[i]
    index_i = file_index[i]


whitefield_fnam = Path(f'{constants.work}/whitefield/whitefield_run{run:>04}.h5')
assert(whitefield_fnam.is_file())

with h5py.File(whitefield_fnam) as f:
    whitefield = f['whitefield'][()]

whitefield[whitefield == 0] = 1

frames_out = []
for fnam, index in tqdm(zip(fnams_i, index_i)): 
    with h5py.File(fnam) as f:
        mask = f['/data/JF07T32V02/meta/pixel_mask'][()]
        frame = f['/data/JF07T32V02/data'][index]
    
    # scale whitefield
    c = np.sum(mask * whitefield * frame) / np.sum(mask * whitefield**2)
    frame = np.clip((frame - c * whitefield) / (c * whitefield)**0.5, 0, None)

    frame_im, centre = get_xyz.geom_cor(frame)

    frames_out.append(frame_im)

out = np.array(frames_out).astype(np.float32)
np.save(f'frames_{run}.npy', out)
"""
