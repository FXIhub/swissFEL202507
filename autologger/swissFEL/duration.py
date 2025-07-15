from pathlib import Path
import json
import numpy as np
import datetime

class Duration():
    """
    as swissFEL runs at 100 Hz:
        duration (s) = (pulse_id_start - pulse_id_stop) / 100
    """

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if self.heading in row:
                continue

            if 'directory' in row:
                # load scan.json
                fnam = row['directory'] / 'meta/scan.json'

                if fnam.is_file():
                    with open(fnam, 'r') as json_file:
                        d = json.load(json_file)
                        row['scan_json'] = d
                        # list of start, stop ids
                        pids = np.array(d['pulseIds'])
                        duration = (pids.max() - pids.min())/100
                        duration = int(round(duration))
                        row[self.heading] = str(datetime.timedelta(seconds=duration))

                # hacky but do this also for 
                fnam = row['directory'] / 'aux/scan_info_rel.json'

                if fnam.is_file():
                    with open(fnam, 'r') as json_file:
                        d = json.load(json_file)
                        row['scan_info_rel'] = d

                else:
                    err = f'could not find scan file {fnam}'
                    raise ValueError(err) 


