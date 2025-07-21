# conda activate /sf/bernina/applications/mm/envs/sfb312

import numpy as np
import h5py
import hdf5plugin
import argparse
from pathlib import Path
import sys
from tqdm import tqdm

import get_xyz

import constants

class MyFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description="""convert streak x,y coordinates from slab to geometry corrected coordinates"""
    )

    parser.add_argument(
        'run',
        type=int,
        help='run number'
    )

    parser.add_argument(
        '--fnam',
        type=str,
        help='file name of streak file'
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=f'{constants.work}/streaks',
        help='output directory'
    )

    args = parser.parse_args()
    return args


def apply_geom_streaks(streaks):
    x, y, panel_ids, panel_index_to_name, parsed_detector_dict = get_xyz.get_xy_map()

    N, M = x.shape

    streaks_xy = np.zeros_like(streaks)
    for i in tqdm(range(streaks.shape[0])):
        fs0, ss0, fs1, ss1 = streaks[i]

        # get panel index
        ss, fs = int(round(ss0)), int(round(fs0))
        ss = min(N-1, max(0, ss))
        fs = min(M-1, max(0, fs))
        index = panel_ids[ss, fs]

        # get panel name
        name = panel_index_to_name[index]

        # panel dict
        p = parsed_detector_dict[name]

        # corner pos of panel
        cx = p['corner_x']
        cy = p['corner_y']
        c0 = cy + 1J * cx

        # relative ss, fs to corner
        ss0 -= p['min_ss']
        ss1 -= p['min_ss']
        fs0 -= p['min_fs']
        fs1 -= p['min_fs']

        dx = p['fs'][1] + 1J * p['fs'][0]
        dy = p['ss'][1] + 1J * p['ss'][0]

        # get r coordinates of streak
        r0 = ss0 * dy + fs0 * dx + c0
        r1 = ss1 * dy + fs1 * dx + c0

        streaks_xy[i] = [r0.real, r0.imag, r1.real, r1.imag]
    return streaks_xy

if __name__ == '__main__':
    args = get_args()

    if args.fnam is None:
        fnam_in = args.output_dir / f'streaks_run{args.run:>04}.h5'
    else:
        fnam_in = args.fnam 
    print(f'loading streak information from: {fnam_in}')

    with h5py.File(fnam_in) as f:
        streaks = f['fs0_ss0_fs1_ss1_slab'][()]

    streaks_xy = apply_geom_streaks(streaks)


    # write to file
    key = 'fs0_ss0_fs1_ss1_im'
    print(f'writing {key} to {fnam_in}')
    with h5py.File(fnam_in, 'r+') as f:
        if key in f:
            del f[key]

        f[key] = streaks_xy


    

