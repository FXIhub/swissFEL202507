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
        description="""Push tabulated text file to a google sheet"""
    )

    parser.add_argument(
        'table',
        type=str,
        help='file name text file containing row data'
    )

    parser.add_argument(
        '--spreadsheet_id',
        type=str,
        help='spreadsheet id, long string in url'
    )

    parser.add_argument(
        '--sheet_id',
        type=str,
        help='sheet id, short string after "gid" in url'
    )

    parser.add_argument(
        '--separator',
        type=str,
        default=None,
        help='separator for column values in table file'
    )

    parser.add_argument(
        '--comment',
        type=str,
        default='#',
        help='comment symbol in table file'
    )

    args = parser.parse_args()
    return args


def text_to_list(fnam, separator, comment):
    with open(fnam, 'r') as f:
        lines = f.readlines()

    rows = []
    for line in lines:
        if line[0] == args.comment:
            continue
        vals = line.split(args.separator)
        row = []
        for val in vals:
            row.append(val.strip())
        rows.append(row)
    return rows


if __name__ == '__main__':
    args = get_args()

    rows = text_to_list(args.table, args.separator, args.comment)

    update_google_sheet.batch_update_values(
            args.spreadsheet_id,
            args.sheet_id,
            rows
    )
