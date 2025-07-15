from pathlib import Path
from time import strftime, localtime


class Date():
    """Depends on run_number"""

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if self.heading in row:
                continue

            # srun_table will have more recent information in it
            if 'swiss_row' in row:
                if 'metadata.time' in row['swiss_row']:
                    ctime = row['swiss_row']['metadata.time']
                    ctime = ctime.timestamp()
            else:
                if 'directory' not in row:
                    continue

                d = row['directory']

                ctime = d.stat().st_ctime

            date = strftime('%Y-%m-%d %H:%M:%S', localtime(ctime))

            row[self.heading] = date

