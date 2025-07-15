import argparse
import runpy
from pathlib import Path
import subprocess
import time

class MyFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description="""Run autologger"""
    )

    parser.add_argument(
        'config',
        type=Path,
        help='python configuration file for run table'
    )

    args = parser.parse_args()
    args.config = args.config.resolve()
    return args


def list_to_text(fnam, rows, separator):
    with open(fnam, 'w') as f:
        for row in rows:
            # convert to str
            t = [str(c) for c in row]
            line = separator.join(t) + '\n'
            f.write(line)
    return True


def nested_dict_to_rows(headings, rows):
    # convert rows to list of lists
    table_list = []
    table_list.append(headings)
    ns = sorted(rows.keys())
    for run_number in ns:
        r = rows[run_number]
        r_list = []
        for h in headings:
            if h in r:
                r_list.append(r[h])
            else:
                r_list.append(None)

        table_list.append(r_list)

    return table_list


if __name__ == '__main__':
    args = get_args()
    config = runpy.run_path(args.config)

    columns = config['columns']
    info = config['info']
    run_loop = config['run_loop']
    separator = info['separator']

    headings = [c.heading for c in columns]
    headings_index = list(range(len(headings)))

    rows = {}

    while True:
        # run once per loop
        run_loop.get(info)

        for c in columns:
            c.get(rows)
            # print(i, rows)

        table_list = nested_dict_to_rows(headings, rows)

        # write table to file as text
        list_to_text(info['run_table'], table_list, separator)

        # push to google
        # usage: push_table.py [-h] [--spreadsheet_id SPREADSHEET_ID] [--sheet_id SHEET_ID] [--separator SEPARATOR] [--comment COMMENT] table
        subprocess.call(f"python google_sheets_push/src/push_table.py --spreadsheet_id={info['spreadsheet_id']} $'--separator={separator}' {info['run_table']}", shell=True)

        time.sleep(5)
