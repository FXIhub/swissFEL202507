import swissFEL

info = {
    'experiment_directory': '/sf/bernina/exp/25g_chapman'
    'spreadsheet_id': '1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE'
    'sheet_id': '0'
    }

# column title: class for getting info
columns = {
    'Run number': swissFEL.Run_number(info),
    'Date': swissFEL.Date(info),
    'Start Time': swissFEL.Start_time(info),
    'Duration': swissFEL.Duration(info),
    'Run Type': swissFEL.Run_type(info),
    'Sample': swissFEL.Sample(info),
    'Num Pulses': swissFEL.Num_pulses(info),
    'Comments': swissFEL.Num_pulses(info)
    }
