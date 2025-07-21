from pathlib import Path
import h5py
import numpy as np

class Num_hits():
    """
    could be expensive
    so update new runs first
    and old runs more slowly
    """

    def __init__(self, info, heading, min_streaks=15):
        self.heading = heading
        self.info = info
        self.min_streaks = min_streaks

    def get(self, rows):
        for n in rows:
            row = rows[n]

            fnam1 = Path(self.info['experiment_directory']) / f'work/streaks/streaks_run{n:>04}.h5'
            fnam2 = Path(self.info['experiment_directory']) / f'work/streaks_ahmed/streaks_run{n:>04}.h5'

            fnam = None
            if fnam2.is_file():

                fnams = Path(self.info['experiment_directory']) / f'work/streaks_ahmed/'
                fnams = fnams.glob(f'streaks_run{n:>04}_file*')
                num_hits = 0
                for fnam in fnams:
                    with h5py.File(fnam) as f:
                        if 'streak_ids' in f:
                            pid = f['streak_ids'][()]
                            _, streaks_d = np.unique(pid, return_counts=True)
                            num_hits += np.sum(streaks_d > self.min_streaks)

                row[self.heading] = num_hits

            elif fnam1.is_file():
                with h5py.File(fnam1) as f:
                    if 'pulse_id' in f:
                        pid = f['pulse_id'][()]
                        _, streaks_d = np.unique(pid, return_counts=True)
                        row[self.heading] = np.sum(streaks_d > self.min_streaks)



