
class Transmission():

    def __init__(self, info, heading):
        self.heading = heading
        self.info = info

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if 'swiss_row' in row:
                srow = row['swiss_row']

                # get two transmission values
                if (
                        'att_usd.readback' in srow
                        and 'att._transmission_fund' in srow
                        ):
                    t1 = srow['att_usd.readback']
                    t2 = srow['att._transmission_fund']
                    row[self.heading] = t1 * t2  # f'{t1 * t2:.2e}'


