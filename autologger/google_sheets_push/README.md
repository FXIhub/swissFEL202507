# google_sheets_push

Push tabulated data in a text file to a google spread sheet

### Create table of values
Create a text file, `table.txt`:
```
# run table generated from another script
run number, hits, duration (s)
1, 100, 120
2, 33, 60
3, 234, 63
```

### Push to spread sheet
```
$ push_table.py table.txt --spreadsheet_id 1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE --sheet_id 0
```

### Pull from spread sheet
Get a text file in the same format (but missing the comments)
```
$ pull_table.py test.txt --spreadsheet_id 1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE --sheet_id 0
```

### Install
```
git clone git@github.com:andyofmelbourne/google_sheets_push.git
cd google_sheets_push
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
export PATH=$(pwd)/src:$PATH
```

### get google token.json file
- go to https://console.developers.google.com
- click "select a project" or existing project name 
- then find the "new project" button and create project e.g. "test"
- then do some more clicking to select the project and note the project number: 770379772789, and project ID: nimble-autumn-463908-n5 in my case
- three lines menu (top left) - apis and services - + enable apis and services - search sheets - click "google sheets API"p - click "Enable"
- maybe redundant
    - click on "OAuth consent screen" (https://console.cloud.google.com/auth), then "Get started"
    - App name: "autologger"
    - Audience: "External"
    - click "Create"
- get lost then find your way to the api's dashboard (https://console.cloud.google.com/apis)
- click "Credentials" on left
- click "+ Create credentials" then "OAuth client ID"
    - Application type: Desktop app
    - Name: me
    - Client ID = "7703797727...apps.googleusercontent.com"
    - Clinet secret = "GOC...RbZ"
    - download JSON = `client_secret_...apps.googleusercontent.com.json`
    - rename = `mv client_secret_...apps.googleusercontent.com.json credentials/credentials.json`
- click "Data access" on left
    - click "Add or remove scopes"
    - select "See, edit, create and delete all your Google Sheets spreadsheets"
    - save
- click "Audience" on left
    - click "+ Add users"
    - enter gmail account of any users, then save
- `python src/authenticate_google.py` which launches a browser, then click OK and continue a few times to produce a `token.json` file
- `mv token.json credentials`
- now `python stc/test.py` should print names from an online spreadsheet
    
google link for this stuff: https://developers.google.com/workspace/sheets/api/quickstart/python

### Create Spreadsheet
- make a spread sheet in google drive, e.g. `test sheet`
- note the url: `https://docs.google.com/spreadsheets/d/1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE/edit?gid=0#gid=0`
- Here:
    - spreadsheet id = `1YzBrLN3aDanu4JOdso_ZwmYtY1mUt2wibBRgowMV_aE`
    - sheet id       = `0` (number after "gid")
