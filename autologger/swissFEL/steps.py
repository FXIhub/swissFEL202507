
class Steps():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if 'swiss_row' in row:
                srow = row['swiss_row']

                # get two transmission values
                if ('metadata.steps' in srow):
                    steps = int(srow['metadata.steps'])
                    row[self.heading] = steps



