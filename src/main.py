import os
import csv


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]   # This is the perminssions of the application (we asking google for permission)

SPREADSHEET_ID = "1eG9NwIeVN4hBqW0B3vhwIN4ewd1cFyeMSBbTgA3oPL4"   # right now this is the sample spreadsheet


def main():
    credentials = None
    if os.path.exists("tokens.json"):
        credentials = Credentials.from_authorized_user_file("tokens.json", SCOPES)   # loading credentials from the token file to not have to do it multiple times
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:   # takes place when there are no available credentials
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("tokens.json", "w") as token:   # creating the token JSON file that did not exist before
            token.write(credentials.to_json())

    try:
        service = build("sheets", "v4", credentials=credentials)   # creating the service to interact with Google Sheets
        sheets = service.spreadsheets()

        results = sheets.values().get(spreadsheetId = SPREADSHEET_ID, range="Sheet1!A1:C6").execute()

        values = results.get("values", [])

        for row in values:
            print(row)

        if not values:
            print("No data found.")
            return

        with open("data.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(values)
        print("Data exported to output.csv")    
    except HttpError as e:
        print(e)

    
if __name__ == "__main__":
    main()
     