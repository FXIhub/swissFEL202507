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
        description="""collect powder files for run and merge"""
    )

    parser.add_argument(
        'run',
        type=int,
        help='run number'
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=f'{constants.work}/powder',
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
    s = f'powder_run{args.run:>04}_file*.h5'
    fnams = sorted(list(args.output_dir.glob(s)))

    print(f'found {len(fnams)} powder files for run {args.run}', file=sys.stderr)

    fnam_out = args.output_dir / f'powder_run{args.run:>04}.h5'
    print(f'outputing powder information to: {fnam_out}')


    powder = None
    counts = 0

    for fnam in fnams:
        with h5py.File(fnam) as f:
            powder_n = f['data'][()]
            if powder is None:
                powder = powder_n
            else:
                powder += powder_n

            counts += f['counts'][()]

        # remove file
        fnam.unlink()

    with h5py.File(fnam_out, 'w') as f:
        f['powder'] = powder / len(fnams)
        f['counts'] = counts
