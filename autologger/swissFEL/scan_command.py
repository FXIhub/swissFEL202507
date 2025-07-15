
class Scan_command():

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
                row[self.heading] = cmd



