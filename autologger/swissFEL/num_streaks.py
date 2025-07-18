from pathlib import Path
import h5py

class Num_streaks():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            fnam = Path(self.info['experiment_directory']) / f'work/streaks/streaks_run{n:>04}.h5'

            if fnam.is_file():
                try: 
                    with h5py.File(fnam) as f:
                        N = f['/counts'].shape[0]
                    row[self.heading] = N
                except:
                    pass
