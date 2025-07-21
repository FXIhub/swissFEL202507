from pathlib import Path
import h5py


class Num_streaks():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            fnam1 = Path(self.info['experiment_directory']) / f'work/streaks/streaks_run{n:>04}.h5'
            fnam2 = Path(self.info['experiment_directory']) / f'work/streaks_ahmed/streaks_run{n:>04}.h5'

            fnam = None
            if fnam2.is_file():
                fnam = fnam2
            elif fnam1.is_file():
                fnam = fnam1

            if fnam is not None:
                try: 
                    with h5py.File(fnam) as f:
                        N = f['/counts'].shape[0]
                    row[self.heading] = N
                except:
                    pass
