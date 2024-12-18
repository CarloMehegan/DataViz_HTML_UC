import os
import csv


from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]   # This is the perminssions of the application (we asking google for permission)

SPREADSHEET_ID = "YOUR_SPREADSHEET_ID_HERE"   # private google sheets ID here


# Page (Sheet) names to process
PAGES = {
    "Occupancy": "occupancy",
    "Table Games": "table_games",
    "Video Games": "video_games",
    "Board & Card Games": "board_games"
}


def get_current_semester():
    """
    Determine the current semester based on the month.
    - Spring: January to May -> spYY
    - Summer: June to August -> suYY
    - Fall: September to December -> fYY
    """
    month = datetime.now().month
    year = str(datetime.now().year)[-2:]  # Extract last two digits of the year

    if month in [1, 2, 3, 4, 5]:
        return f"s{year}"  # Spring
    else:
        return f"f{year}"  # Fall


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
        # Build the Google Sheets service
        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        # Get current semester abbreviation (e.g., f23)
        semester = get_current_semester()

        # Ensure the 'raw_data' folder exists
        raw_data_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "raw_data")
        if not os.path.exists(raw_data_folder):
            os.makedirs(raw_data_folder)

        # Process each page (sheet) and export to its own CSV
        for page_name, clean_name in PAGES.items():
            print(f"Processing page: {page_name}")

            # Fetch all data in the specified sheet
            results = sheets.values().get(spreadsheetId=SPREADSHEET_ID, range=page_name).execute() 
            values = results.get("values", [])

            if not values:
                print(f"No data found in '{page_name}'.")
                continue

            # Generate a CSV file name and set its path inside 'raw_data' folder
            output_file = os.path.join(raw_data_folder, f"{semester}_{clean_name}_raw.csv")

            # Write data to the CSV file
            with open(output_file, "w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(values)

            print(f"Data exported to {output_file}")  
    except HttpError as e:
        print(e)

    
if __name__ == "__main__":
    main()
     