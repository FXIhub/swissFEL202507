from pathlib import Path

class Run_number():

    def __init__(self, info, heading):
        self.run_dir = Path(info['experiment_directory']) / 'raw'

        # check if the directory exists
        if not self.run_dir.is_dir():
            err = f'could not find directory {self.run_dir}'
            raise ValueError(err)

        self.heading = heading

    def get(self, rows):
        runs = sorted(self.run_dir.glob('run*'))
        for run in runs:
            if not run.is_dir():
                continue

            if not len(run.stem) == 7:
                continue

            try:
                n = int(run.stem[p-4:])
            except ValueError:
                continue

            if n not in rows:
                rows[n] = {}

            if self.heading not in rows[n]:
                rows[n][self.heading] = n
