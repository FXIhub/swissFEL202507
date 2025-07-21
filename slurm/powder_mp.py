import numpy as np
import h5py
import hdf5plugin
import argparse
from pathlib import Path
import sys
from tqdm import tqdm

import multiprocessing as mp

import constants


class MyFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description="""generate powder pattern"""
    )

    parser.add_argument(
        'run',
        type=int,
        help='run number'
    )

    parser.add_argument(
        '--maxframes',
        type=int,
        help='maximum number of frames to process'
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=f'{constants.work}/powder',
        help='output directory'
    )

    args = parser.parse_args()
    return args


class Powder():

    def __init__(self, fnams, shape, nproc=1):
        self.fnams = fnams
        self.shape = shape
        self.nproc = nproc

        # get files for each process to process
        self.fnam_inds = np.linspace(0, len(fnams), nproc+1).astype(int)
        print(f'indices to process: {self.fnam_inds}')

    def run(self):
        pool = mp.Pool(self.nproc)

        result_iter = pool.imap_unordered(
                self.run_worker, range(self.nproc)
                )

        powder = np.zeros(self.shape)
        counts = 0
        for powder_n, counts_n in result_iter:
            powder += powder_n
            counts += counts_n

        return powder, counts

    def run_worker(self, n):
        # only show progress for the last process
        if n == (self.nproc-1):
            disable = False
        else:
            disable = True

        powder = np.zeros(self.shape)
        counts = 0

        i0 = self.fnam_inds[n] 
        i1 = self.fnam_inds[n+1]
        for fnam in self.fnams[i0:i1]:
            print('processing:', fnam)
            with h5py.File(fnam) as f:
                data = f['/data/JF07T32V02/data']

                for d in tqdm(range(data.shape[0]), disable=disable):
                    powder += data[d]
                    counts += 1

        return powder, counts



if __name__ == '__main__':
    args = get_args()

    # check that that output dir exists
    print(f'outputdir={args.output_dir}', file=sys.stderr)
    assert(args.output_dir.is_dir())

    # check that input dir exists
    run_dir = Path(f'{constants.raw}/run{args.run:>04}/data')
    assert(run_dir.is_dir())

    # get file list
    fnams = list(run_dir.glob('acq*.JF07T32V02.h5'))

    print(f'found {len(fnams)} Junfrau files in run directory: {run_dir}', file=sys.stderr)

    with h5py.File(fnams[0]) as f:
        shape = f['/data/JF07T32V02/data'].shape[1:]

    a = Powder(fnams, shape)
    powder, count = a.run()

    out = args.output_dir / f'powder_run{args.run:>04}.h5'

    with h5py.File(out, 'w') as f:
        f['data'] = powder / counts
        f['counts'] = counts

