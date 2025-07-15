
class Name():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if (
                    'scan_json' in row
                    and 'scan_name' in row['scan_json']
                ):
                
                name = row['scan_name']

            elif (
                    'swiss_row' in row
                    and 'metadata.time' in row['swiss_row']
                ):

                name = row['swiss_row']['metadata.name']

            else:
                name = None

            if name is not None:
                row[self.heading] = name

