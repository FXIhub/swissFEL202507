import swissFEL

# meta data
info = {
    'experiment_directory': '/sf/bernina/exp/25g_chapman',
    'spreadsheet_id': '1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE',
    'sheet_id': '0',
    'run_table': 'table.txt',
    }

# google_link = 'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?gid={sheet_id}#gid={sheet_id}',

# column title: class for getting info
# each function gets info headings and rows. Then updates rows inplace.
# e.g. swissFEL.Run_number.get(headings, rows, info)
columns = [
    swissFEL.Run_number(info, 'Run number'),
    # 'Date': swissFEL.Date(info),
    # 'Start Time': swissFEL.Start_time(info),
    # 'Duration': swissFEL.Duration(info),
    # 'Run Type': swissFEL.Run_type(info),
    # 'Sample': swissFEL.Sample(info),
    # 'Num Pulses': swissFEL.Num_pulses(info),
    # 'Comments': swissFEL.Num_pulses(info)
    ]

rows = {}

for i in range(10):
    for c in columns:
        c.get(rows)
        print(i, rows)

