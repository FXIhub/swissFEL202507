import numpy as np
import h5py
import hdf5plugin
import argparse
from pathlib import Path
import sys
from tqdm import tqdm

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

    parser.add_argument(
        '--file_index',
        type=int,
        default=1,
        help="process the file_index'th in run directory (counting from 1)"
    )

    args = parser.parse_args()
    return args


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
    fnam = fnams[args.file_index-1]
    if args.file_index == 0:
        disable = False
    else:
        disable = True

    print(f'found {len(fnams)} Junfrau files in run directory: {run_dir}', file=sys.stderr)

    with h5py.File(fnams[0]) as f:
        shape = f['/data/JF07T32V02/data'].shape[1:]

    powder = np.zeros(shape)
    counts = 0

    with h5py.File(fnam) as f:
        data = f['/data/JF07T32V02/data']
        # mask = f['/data/JF07T32V02/meta/pixel_mask'][()]
        # mask = mask.astype(bool)

        for d in tqdm(range(data.shape[0]), desc=f'processing {fnam}', disable=disable):
            powder += data[d]
            counts += 1

    fnam_out = args.output_dir / f'powder_run{args.run:>04}_file{args.file_index:>04}.h5'
    print(f'outputing powder information to: {fnam_out}')

    with h5py.File(fnam_out, 'w') as f:
        f['data'] = powder / counts
        f['counts'] = counts

