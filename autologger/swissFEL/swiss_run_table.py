import pickle
from pathlib import Path

class Load_swiss_run_table():

    def __init__(self, info):
        fnam = Path(info['swiss_run_table'])

        if not fnam.is_file():
            print(f'cannot find {fnam}. skipping swissfel run table')
            self.fnam = None
        else:
            self.fnam = fnam

    def get(self, info):
        # load swissFEL run_table if it exists
        if self.fnam:
            with open(self.fnam, 'rb') as f:
                info['swiss_run_table'] = pickle.load(f)
