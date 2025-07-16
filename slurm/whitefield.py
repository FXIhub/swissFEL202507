import numpy as np
import streak_finder as sf
import h5py
import hdf5plugin
import argparse
from pathlib import Path
import sys
from tqdm import tqdm
import json

import constants

class MyFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description="""calculate whitefield"""
    )

    parser.add_argument(
        'run',
        type=int,
        help='run number'
    )

    parser.add_argument(
        '--maxframes',
        type=int,
        default=50,
        help='maximum number of frames to process'
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=f'{constants.work}/whitefield',
        help='output directory'
    )

    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = get_args()

    print(f'processing run: {args.run}', file=sys.stderr)

    # check that that output dir exists
    assert(args.output_dir.is_dir())

    # check that input dir exists
    run_dir = Path(f'{constants.raw}/run{args.run:>04}/data')
    assert(run_dir.is_dir())

    # get file list
    fnams = list(run_dir.glob('acq*.JF07T32V02.h5'))
    fnam = fnams[0]

    print(f'found {len(fnams)} Junfrau files in run directory: {run_dir}', file=sys.stderr)
    
    out_fnam = args.output_dir / f'whitefield_run{args.run:>04}.h5'

    with h5py.File(fnam) as f:
        data = f['/data/JF07T32V02/data']

        inds = np.linspace(0, data.shape[0]-1, args.maxframes).astype(int)

        t = np.empty((args.maxframes,) + data.shape[1:], dtype=float)
        for i, d in tqdm(enumerate(inds), desc='loading data'):
            t[i] = data[d]
   
    print('calling update_whitefield', file=sys.stderr)
    cryst_data = sf.CrystData(data=t)
    cryst_data = cryst_data.update_whitefield(method='robust-mean', r0=0.25, r1=0.99, num_threads=32)
    cryst_data.whitefield = np.clip(cryst_data.whitefield, 0, np.inf)
    cryst_data = cryst_data.update_std(method='poisson')

    with h5py.File(out_fnam, 'w') as f:
        f['whitefield'] = cryst_data.whitefield
        f['std'] = cryst_data.std
