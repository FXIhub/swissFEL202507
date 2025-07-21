import swissFEL

# meta data
info = {
    'experiment_directory': '/sf/bernina/exp/25g_chapman',
    'spreadsheet_id': '1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE',
    'sheet_id': '0',
    'run_table': 'table.txt',
    'swiss_run_table': '/sf/bernina/exp/25g_chapman/res/run_data/run_table/p22263_runtable.pkl',
    'separator': ';'
    }

# google_link = 'https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit?gid={sheet_id}#gid={sheet_id}',

# each class object must have a 'get' method that takes a rows argument
# which is dict of dicts
# rows = {
#   1: {'Run number': 1, 'Date': '1/2/2025', ...}
#   3: {'Run number': 3, 'Date': '2/2/2025', ...}
# }
# Then updates rows inplace.
# e.g. swissFEL.Run_number.get(rows)
columns = [
    swissFEL.Run_number(info, 'Run number'),
    swissFEL.Date(info, 'Date'),
    swissFEL.Duration(info, 'Duration'),
    swissFEL.Name(info, 'Scan name'),
    swissFEL.Description(info, 'Scan description'),
    swissFEL.Pulses(info, 'Pulses'),
    swissFEL.Transmission(info, 'Transmission'),
    swissFEL.Steps(info, 'Steps'),
    swissFEL.Num_hits(info, 'Num hits'),
    swissFEL.Hit_rate(info, 'Hit fraction'),
    swissFEL.Num_streaks(info, 'Num streaks'),
    swissFEL.Scan_command(info, 'Command'),
    # 'Start Time': swissFEL.Start_time(info),
    # 'Run Type': swissFEL.Run_type(info),
    # 'Sample': swissFEL.Sample(info),
    # 'Num Pulses': swissFEL.Num_pulses(info),
    # 'Comments': swissFEL.Num_pulses(info)
    ]

# script to run every loop
run_loop = swissFEL.Load_swiss_run_table(info)

# script to run every row (for every run)
# run_row = swissFEL.Load_meta_data(info, row)
