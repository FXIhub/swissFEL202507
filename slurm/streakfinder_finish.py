import numpy as np
import h5py
import hdf5plugin
import argparse
from pathlib import Path
import sys

import constants

class MyFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description="""collect streak files for run and merge"""
    )

    parser.add_argument(
        'run',
        type=int,
        help='run number'
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=f'{constants.work}/streaks',
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

    # check streak files
    s = f'streaks_run{args.run:>04}_file*.h5'
    fnams = sorted(list(args.output_dir.glob(s)))

    print(f'found {len(fnams)} sreak files for run {args.run}', file=sys.stderr)

    fnam_out = args.output_dir / f'streaks_run{args.run:>04}.h5'
    print(f'outputing streak information to: {fnam_out}')

    lines = []
    counts = []
    pids = []
    file_index = []
    file_name = []
    for fnam in fnams:
        with h5py.File(fnam) as f:
            N = f['streaks'].shape[0]
            lines.append(f['streaks'][()])
            counts.append(f['counts'][()])
            pids.append(f['pulse_id'][()])
            file_index.append(f['file_index'][()])
            t = N * [f['file_name'][()].decode()]
            file_name += t

        # remove file
        fnam.unlink()

    with h5py.File(fnam_out, 'w') as f:
        f['fs0_ss0_fs1_ss1_slab'] = np.concatenate(lines, axis=0)
        f['counts'] = np.concatenate(counts, axis=0)
        f['pulse_id'] = np.concatenate(pids, axis=0)
        f['file_index'] = np.concatenate(file_index, axis=0)
        f['file_name'] = np.array(file_name, dtype='S')
