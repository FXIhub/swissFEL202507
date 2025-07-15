#!/usr/bin/env python3

import sys
import update_google_sheet
import argparse

class MyFormatter(
    argparse.ArgumentDefaultsHelpFormatter,
    argparse.RawDescriptionHelpFormatter
):
    pass

def get_args():
    parser = argparse.ArgumentParser(
        formatter_class=MyFormatter,
        description="""Pull tabulated text file from a google sheet"""
    )

    parser.add_argument(
        'table',
        type=str,
        help='output file name, text file will contain row data'
    )

    parser.add_argument(
        '--spreadsheet_id',
        type=str,
        help='spreadsheet id, long string in url'
    )

    parser.add_argument(
        '--sheet_id',
        type=int,
        help='sheet id, short string after "gid" in url'
    )

    parser.add_argument(
        '--separator',
        type=str,
        default=',',
        help="separator for column values in table file. "\
        "Use $'--separator=\\t' to escape tab or newline characters"
    )

    args = parser.parse_args()
    return args


def list_to_text(fnam, rows, separator):
    with open(fnam, 'w') as f:
        for row in rows:
            # convert to str
            t = [str(c) for c in row]
            line = separator.join(t) + '\n'
            f.write(line)
    return True


if __name__ == '__main__':
    args = get_args()

    rows = update_google_sheet.pull_values(
            args.spreadsheet_id,
            args.sheet_id
    )

    for row in rows:
        print(row)

    list_to_text(args.table, rows, args.separator)
