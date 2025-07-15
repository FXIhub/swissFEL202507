import authenticate_google
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import numpy as np

def pull_values(
        spreadsheet_id,
        sheet_id,
        fill_empty=''
    ):
    creds = authenticate_google.get()

    try:
        service = build("sheets", "v4", credentials=creds)

        sheet = service.spreadsheets()

        # get Sheet title and index
        fields = 'sheets(data/rowData/values/userEnteredValue,properties(index,sheetId,title))'
        res = sheet.get(
                spreadsheetId=spreadsheet_id,
                fields=fields
        ).execute()

        title = None
        index = None
        rows = []
        for sheet in res['sheets']:
            if sheet['properties']['sheetId'] == sheet_id:
                title = sheet['properties']['title']
                index = sheet['properties']['index']

                # I don't know what would be in other indices
                data = sheet['data'][0]
                if 'rowData' in data:
                    for grow in data['rowData']:
                        row = []
                        if 'values' in grow:
                            for cell in grow['values']:
                                if 'userEnteredValue' in cell:
                                    uev = cell['userEnteredValue']

                                    if 'stringValue' in uev:
                                        row.append(uev['stringValue'])
                                    elif 'numberValue' in uev:
                                        row.append(uev['numberValue'])
                                    else:
                                        err = f'could not parse cell value {uev=}'
                                        raise ValueError(err)
                                else:
                                    # empty cell
                                    row.append(fill_empty)
                        else:
                            # empty row
                            rows.append([])

                        rows.append(row)
                else:
                    # empty sheet
                    pass

        if title is None:
            err = f'Error: could not find sub-sheet with id {sheet_id}'
            raise ValueError(err)

        if len(rows) == 0:
            err = f'Warning: no data found in {title=} {sheet_id=}'
            print(err)

    except HttpError as err:
        print(err)
        rows = None

    return rows


def batch_update_values(
        spreadsheet_id,
        sheet_id,
        data,
        col_start=0,
        row_start=0
    ):
    """
    writes a list of lists values to sheets starting at column col_start and row row_start
    """
    creds = authenticate_google.get()

    # make input for batch update
    # I wish I could use service.spreadsheets().values().batchUpdate
    # but I can't figure out how to add a sheet id to this
    # https://stackoverflow.com/questions/64099894/python-google-sheets-api-make-values-update-and-sheet-properties-update-with-a-s
    rows = []
    for r in data:
        col = []
        for c in r:
            col.append({"userEnteredValue": ({"numberValue": c} if str(c).replace('.', '', 1).isdigit() else {"stringValue": c})})
            #col.append({"userEnteredValue": ({"stringValue": str(c)})})
        rows.append({"values": col})

    # https://stackoverflow.com/questions/50916422/python-typeerror-object-of-type-int64-is-not-json-serializable
    #rows = json.dumps(rows, cls=NpEncoder)
    body = {
    "requests": [
        {
            "updateCells": {
                "start": {
                    "sheetId": sheet_id,
                    "rowIndex": row_start,
                    "columnIndex": col_start
                },
                "rows": rows,
                "fields": "userEnteredValue"
            }
        }
    ]
    }
    try:
        service = build("sheets", "v4", credentials=creds)

        result = (
            service.spreadsheets()
            .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
            .execute()
        )

        print(f"{(result.get('totalUpdatedCells'))} cells updated.")
        return result

    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

if __name__ == '__main__':
    spreadsheet_id = "1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE"
    sheet_id       = "0"
    headings = ['heading 1', 'heading 2']
    values = [['a', 2], ['c', None]]
    batch_update_values(spreadsheet_id, sheet_id, headings, values, col_start=5)
