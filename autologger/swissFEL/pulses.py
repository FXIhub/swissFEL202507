import numpy as np

class Pulses():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if 'scan_json' in row:
                d = row['scan_json']
                pids = np.array(d['pulseIds'])
                pulses = np.max(pids) - np.min(pids)
                read = np.sum(np.diff(pids, axis=1))
                dead = pulses - read
                row[self.heading] = f'{pulses} {read} {dead}'

