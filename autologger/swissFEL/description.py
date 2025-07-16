import numpy as np

class Description():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if (
                    'swiss_row' in row
                    and 'metadata.scan_command' in row['swiss_row']
                ):

                cmd = row['swiss_row']['metadata.scan_command']
                cmd = cmd.replace("'", '"')
                print(f'{cmd=}')
                cmd = cmd.split('"')
                i = np.where(['description' in c for c in cmd])[0][0]+1
                desc = cmd[i]
                row[self.heading] = desc

            elif (
                    'scan_info_rel' in row
                    and 'scan_description' in row['scan_info_rel']
                    ):
                desc = row['scan_info_rel']['scan_description']
                row[self.heading] = desc


