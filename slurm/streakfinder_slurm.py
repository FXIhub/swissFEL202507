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
        '--file_index',
        type=int,
        default=1,
        help="process the file_index'th in run directory (counting from 1)"
    )

    parser.add_argument(
        '--mask_file',
        type=Path,
        default=Path(f'{constants.work}/mask/mask_hist_man_dil_am.h5'),
        help="mask file (h5) in slab format (16448, 1030)"
    )

    parser.add_argument(
        '--mask_file_path',
        type=str,
        default='data/data',
        help="path to mask data in mask file."
    )

    parser.add_argument(
        '--output_dir',
        type=Path,
        default=f'{constants.work}/streaks',
        help='output directory'
    )

    args = parser.parse_args()
    return args


class Streaks():

    def __init__(self, fnam, mask, whitefield, pid, params, nproc=40):
        self.mask = mask
        self.whitefield = whitefield
        self.pid = pid
        self.params = params
        self.nproc = nproc

        # get number of frames to process
        with h5py.File(fnam) as f:
            data = f['/data/JF07T32V02/data']
            self.D = data.shape[0]

        # get indices for each process to process
        self.frame_inds = np.linspace(0, self.D, nproc+1).astype(int)
        print(f'indices to process: {self.frame_inds}')

    def run(self):
        pool = mp.Pool(self.nproc)

        result_iter = pool.imap_unordered(
                self.run_worker, range(self.nproc)
                )

        lines = []
        pids = []
        inds = []
        counts = []
        for lines_n, pids_n, inds_n, counts_n in result_iter:
            lines += lines_n
            pids += pids_n
            inds += inds_n
            counts += counts_n

        lines = np.concatenate(lines, axis=0)
        counts = np.concatenate(counts, axis=0)
        return lines, np.array(pids), np.array(inds), counts

    def run_worker(self, n):
        # only show progress for the last process
        # if d == (self.D-1):
        #     disable = False
        # else:
        #     disable = True

        params = self.params
        mask = self.mask
        whitefield = self.whitefield

        lines = []
        pids = []
        inds = []
        counts = []

        with h5py.File(fnam) as f:
            data = f['/data/JF07T32V02/data']
            for d in range(self.frame_inds[n], self.frame_inds[n+1]):
                print(f'processing frame {d}')
                sys.stdout.flush()

                # out = np.sum(data[d])
                frame = data[d]
                # scale whitefield
                c = np.sum(mask * whitefield * frame) / np.sum(mask * whitefield**2)
                frame = np.clip((frame - c * whitefield) / (c * whitefield)**0.5, 0, None)

                det_obj = sf.streak_finder.PatternStreakFinder(data=frame, mask=mask, structure=params.streaks.structure.to_structure('2d'),
                                                               min_size=params.streaks.min_size, nfa=params.streaks.nfa)

                peaks = det_obj.detect_peaks(vmin=params.peaks.vmin, npts=params.peaks.npts, connectivity=params.peaks.structure.to_structure('2d'),
                                             num_threads=1)

                streaks = det_obj.detect_streaks(peaks, xtol=params.streaks.xtol, vmin=params.streaks.vmin, num_threads=1)

                t = streaks[0].to_lines() # (num_streaks, 4) numpy array

                regions = streaks[0].to_regions()

                N = t.shape[0]
                if N > 0:
                    lines.append(t)
                    pids += N * [pid[d]]
                    inds += N * [d]
                    counts.append(sf.label.total_mass(regions, frame)) # (num_streaks,) numpy array

        return lines, pids, inds, counts

if __name__ == '__main__':
    args = get_args()

    print(f'processing run: {args.run}', file=sys.stderr)

    # check that that output dir exists
    assert(args.output_dir.is_dir())

    # check that input dir exists
    run_dir = Path(f'{constants.raw}/run{args.run:>04}/data')
    assert(run_dir.is_dir())

    # get file list
    fnams = sorted(list(run_dir.glob('acq*.JF07T32V02.h5')))

    print(f'found {len(fnams)} Junfrau files in run directory: {run_dir}', file=sys.stderr)

    # check whitefield
    whitefield_fnam = Path(f'{constants.work}/whitefield/whitefield_run{args.run:>04}.h5')
    assert(whitefield_fnam.is_file())

    with h5py.File(whitefield_fnam) as f:
        whitefield = f['whitefield'][()]

    whitefield[whitefield == 0] = 1

    fnam = fnams[args.file_index-1]

    with h5py.File(fnam) as f:
        pid = f['/data/JF07T32V02/pulse_id'][()]
        mask = f['/data/JF07T32V02/meta/pixel_mask'][()]
        mask = mask.astype(bool)

    # combine with user selected mask   
    with h5py.File(args.mask_file) as f:
        mask *= f[args.mask_file_path][()].astype(bool)

    params = sf.scripts.StreakFinderParameters.read(args.params_file, 'json')
    streaks = Streaks(fnam, mask, whitefield, pid, params)

    lines, pids, inds, counts = streaks.run()

    fnam_out = args.output_dir / f'streaks_run{args.run:>04}_file{args.file_index:>04}.h5'
    print(f'outputing streak information to: {fnam_out}')

    with h5py.File(fnam_out, 'w') as f:
        f['streaks'] = lines
        f['counts'] = counts
        f['pulse_id'] = np.array(pids)
        f['file_index'] = np.array(inds)
        f['file_name'] = np.array(fnam, dtype='S')

