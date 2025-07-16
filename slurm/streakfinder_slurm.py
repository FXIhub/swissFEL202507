import numpy as np
import streak_finder as sf
from streak_finder.scripts import CrystMetadata, StreakParameters, RegionParameters, StructureParameters, StreakFinderParameters, find_streaks
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
        description="""streak finder"""
    )

    parser.add_argument(
        'run',
        type=int,
        help='run number'
    )

    parser.add_argument(
        '--maxframes',
        type=int,
        default=10000,
        help='maximum number of frames to process'
    )

    parser.add_argument(
        '--params_file',
        type=Path,
        default='streak_finder_params.json',
        help='json file containing streak finder params'
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

    # get file list
    fnams = list(run_dir.glob('acq*.JF07T32V02.h5'))

    print(f'found {len(fnams)} Junfrau files in run directory: {run_dir}', file=sys.stderr)

    # check whitefield
    whitefield_fnam = Path(f'{constants.work}/whitefield/whitefield_run{args.run:>04}.h5')
    assert(whitefield_fnam.is_file())

    with h5py.File(whitefield_fnam) as f:
        whitefield = f['whitefield'][()]

    lines = []
    pids = []
    fnams_out = []
    inds = []
    counts = []
    frames = 0
    for fnam in tqdm(fnams):
        with h5py.File(fnam) as f:
            data = f['/data/JF07T32V02/data']
            pid = f['/data/JF07T32V02/pulse_id']
            mask = f['/data/JF07T32V02/meta/pixel_mask'][()]
            mask = mask.astype(bool)
            # whitefield = np.zeros(data.shape[1:], dtype=float)

            params = sf.scripts.StreakFinderParameters.read(args.params_file, 'json')


            for d in tqdm(range(data.shape[0]), desc=f'processing {fnam}', leave=False):
                frame = np.clip(data[d] - whitefield, 0, None)

                det_obj = sf.streak_finder.PatternStreakFinder(data=frame, mask=mask, structure=params.streaks.structure.to_structure('2d'),
                                                               min_size=params.streaks.min_size, nfa=params.streaks.nfa)

                peaks = det_obj.detect_peaks(vmin=params.peaks.vmin, npts=params.peaks.npts, connectivity=params.peaks.structure.to_structure('2d'),
                                             num_threads=1)

                streaks = det_obj.detect_streaks(peaks, xtol=params.streaks.xtol, vmin=params.streaks.vmin, num_threads=1)
                t = streaks[0].to_lines() # (num_streaks, 4) numpy array

                regions = streaks[0].to_regions()

                frames += 1
                if t.shape[0] > 0:
                    lines.append(t)
                    pids.append(pid[d])
                    inds.append(d)
                    fnams_out.append(fnam)
                    counts.append(sf.label.total_mass(regions, frame)) # (num_streaks,) numpy array

                if frames == args.maxframes:
                    break

        if frames == args.maxframes:
            break

    print(lines)

    lines = np.concatenate(lines, axis=0)
    counts = np.concatenate(counts, axis=0)

    fnam = args.output_dir / f'streaks_run{args.run:>04}.h5'
    print(f'outputing streak information to: {fnam}')
    with h5py.File(fnam, 'w') as f:
        f['streaks'] = lines
        f['counts'] = counts
        f['pulse_id'] = np.array(pids)
        f['file_index'] = np.array(inds)
        f['file_name'] = np.array(fnams_out, dtype='S')


"""
import matplotlib.pyplot as plt
fig, ax = plt.subplots()

ax.imshow(data)
# for line in streaks[0].to_lines():
#     ax.plot(line[::2], line[1::2])

plt.show()
"""

