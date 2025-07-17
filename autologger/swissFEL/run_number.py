from pathlib import Path

class Run_number():

    def __init__(self, info, heading):
        self.run_dir = Path(info['experiment_directory']) / 'raw'

        # check if the directory exists
        if not self.run_dir.is_dir():
            err = f'could not find directory {self.run_dir}'
            raise ValueError(err)

        self.heading = heading
        self.info = info

    def add_row(self, n, rows):
        if n not in rows:
            rows[n] = {}

        if self.heading not in rows[n]:
            rows[n][self.heading] = n


    def get(self, rows):
        # srun_table will have more recent information in it
        self.get_from_swiss_table(rows)
            
        runs = sorted(self.run_dir.glob('run*'))
        for run in runs:
            if not run.is_dir():
                continue

            if not len(run.stem) == 7:
                continue

            try:
                n = int(run.stem[-4:])
            except ValueError:
                continue

            self.add_row(n, rows)

            if 'directory' not in rows[n]:
                rows[n]['directory'] = run


    def get_from_swiss_table(self, rows):
        if 'swiss_run_table' in self.info:
            srun_table = self.info['swiss_run_table']
            # print(f'{srun_table=}')
            runs = srun_table.axes[0]

            for n in runs:
                self.add_row(n, rows)

                rows[n]['swiss_row'] = srun_table.loc[n]
