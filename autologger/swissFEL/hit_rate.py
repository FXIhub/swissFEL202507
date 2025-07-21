class Hit_rate():

    def __init__(self, info, heading, min_streaks=5):
        self.heading = heading
        self.info = info
        self.min_streaks = min_streaks

    def get(self, rows):
        for n in rows:
            row = rows[n]

            if 'Pulses' in row and 'Num hits' in row:
                if row['Pulses'] is not None and row['Pulses'] > 0:
                    row[self.heading] = row['Num hits'] / row['Pulses']


