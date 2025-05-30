import csv
from datetime import datetime

#This file contains clean_games, which cleans the data for the
#video game, table game, and board game spreadsheets.

'''
Steps for cleaning board games
- (UNIQUE) For games that aren't in the spreadsheet's dropdown,the game is listed
  as "Other" and the actual name is listed in the Notes column. To fix this, we
  use the values in the Notes column to fill the Games column, and then remove
  the Notes column.
- Remove empty columns (Board games has 6 real columns)
- Fill date column
- Remove "bad rows" where time values are missing
- Anonymize rows by removing names and student IDs and replacing them with unique IDs
- Fix AM/PM time disparity
- Add "Duration (minutes)" column

Steps for cleaning video games
- (UNIQUE) Fill empty values in the "Game" column with "Unspecified"
- Remove empty columns (Board games has 8 real columns)
- Fill date column
- Remove "bad rows" where time values are missing
- Anonymize rows by removing names and student IDs and replacing them with unique IDs
- Fix AM/PM time disparity
- Add "Duration (minutes)" column

Steps for cleaning table games
- Remove empty columns (Table games has 7 real columns)
- Fill date column
- Remove "bad rows" where time values are missing
- Anonymize rows by removing names and student IDs and replacing them with unique IDs
- Fix AM/PM time disparity
- (UNIQUE) Fill "Table #" column
- (UNIQUE) Fix "Table Game" column using "Table #" (rare edge case)
- Add "Duration (minutes)" column

Steps for cleaning occupancy
- Remove any entries that have missing values
- Fix AM/PM time disparity
- Standardize date formats
'''

#helper functions for reading and writing to csv
def read_csv(file_path):
    with open(file_path, mode='r', newline='') as infile:
        return list(csv.reader(infile))

def save_csv(data, file_path):
    with open(file_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)

def clean_occupancy(raw_filepath,bad_filepath,clean_filepath,year):
    """
    A simpler version of the clean_games function below

    Occupancy is simpler to clean and structured differently from the other tables,
    so we use a different function to clean it
    """

    data = read_csv(raw_filepath)

    print("Parsing CSV at:", raw_filepath)
    data = remove_empty_columns(data, 4) #occupancy has 4 columns
    data = remove_bad_rows_occupancy(data, bad_filepath)

    #fall 2024 handles times differently. AM/PM is actually specified
    if "f24" in raw_filepath:
        flag_out_of_range_am_pm_times(data)
        data = convert_am_pm_times_to_military(data)
    else:
        data = fix_time_disparity_occupancy(data)
    
    data = fill_and_standardize_date_column(data, year, column=1) #occupancy is always 2024

    print("Parsing complete! First 5 rows:")
    for i in range(5):
        print(data[i])

    save_csv(data, clean_filepath)
    print("Cleaned CSV saved to:", clean_filepath)
    pass

#main function to call to clean a file
def clean_games(raw_filepath,
                bad_filepath,
                clean_filepath,
                year,
                type,
                num_columns = -1,
               ):
    """
    Runs all of the parsing steps

    Filepath inputs are most likely:
        "../raw_data/board_games_raw.csv",
        "../raw_data/f23_board_games_bad_rows.csv",
        "../clean_data/f23_board_games_cleaned.csv"
    
    num_columns (int): I'll think of a better name later...?
        All of the spreadsheets tend to have empty/ghost columns at the end.
        This parameter specifies how many columns to keep.
        Columns after this are removed.
    
    fix_notes_column is an extra step for the board game table.
    """
    #defaults for num columns if not specified
    if num_columns == -1:
        match type:
            case "video_games":
                num_columns = 8
            case "board_games":
                num_columns = 6
            case "table_games":
                num_columns = 7

    data = read_csv(raw_filepath)

    print("Parsing CSV at:", raw_filepath)

    #extra step for board games
    if type == "board_games":
        data = resolve_board_game_notes_column(data)
    
    #extra step for video games
    if type == "video_games":
        data = fill_game_column(data)

    data = remove_empty_columns(data, num_columns)
    # data = fill_date_column(data)
    data = fill_and_standardize_date_column(data, year)
    data = remove_bad_rows(data, bad_filepath)
    data = anonymize_rows(data)

    #fall 2024 handles time differently. it actually has am/pm specified
    if "f24" in raw_filepath:
        flag_out_of_range_am_pm_times(data)
        data = convert_am_pm_times_to_military(data)
    else:
        check_invalid_times(data)
        data = fix_time_disparity(data)
    
    data = add_duration_column(data)

    #extra steps for table games
    if type == "table_games":
        data = fill_table_numbers(data)
        data = fill_game_by_pool_table_number(data)

    print("Parsing complete! First 5 rows:")
    for i in range(5):
        print(data[i])

    save_csv(data, clean_filepath)
    print("Cleaned CSV saved to:", clean_filepath)



def resolve_board_game_notes_column(data: list[list[str]]) -> list[list[str]]:
    """
    Replaces 'Other' in the 'Game' column with the value from the 'Notes' column, if available.
    Automatically locates the "Game" and "Notes" columns.

    This was done manually in the original parsing.
    Technically this is "step 0" for board games.
    """
    header = data[0]
    rows = data[1:]

    # Find indices for "Game" and "Notes" columns
    try:
        game_index = header.index("Game")
        notes_index = header.index("Notes")
    except ValueError as e:
        raise ValueError("Required columns 'Game' or 'Notes' are missing.") from e

    resolved_rows = []
    for row in rows:
        if row[game_index].strip().lower() == "other" or row[game_index].strip().lower() == "other (specify in notes)":  # Check if 'Game' column contains 'Other'
            notes_value = row[notes_index].strip()  # Get the value from 'Notes' column
            if notes_value:  # Replace 'Other' if there's a value in 'Notes'
                row[game_index] = notes_value
        resolved_rows.append(row)

    return [header] + resolved_rows


#parsing functions start here
def remove_empty_columns(data: list[list[str]], end_index:int) -> list[list[str]]:
    """
    Removes extra ghost columns and the 'Notes' column from the dataset.

    end_index (int): the last column to include.

    This is "step 1" in the original parsing
    """
    header = data[0][:end_index]  # Keep only the first end_index+1 columns
    rows = [row[:end_index] for row in data[1:]]  # Same for data rows
    return [header] + rows


def fill_date_column(data: list[list[str]]) -> list[list[str]]:
    """
    Fills down missing values in the first column (Date).

    This is "step 2" in the original parsing
    """
    header = data[0]
    rows = data[1:]

    current_date = None
    filled_rows = []
    for row in rows:
        if row[0].strip():  # If the date column is not empty
            current_date = row[0].strip()  # Update the current date
        else:
            row[0] = current_date  # Fill missing date with the current date
        filled_rows.append(row)

    return [header] + filled_rows

def fill_and_standardize_date_column(data: list[list[str]], year: int, column: int = 0) -> list[list[str]]:
    """
    Fills down missing values in the first column (Date) and standardizes all dates
    to 'YYYY-MM-DD' format using the provided year if not specified in the data.
    
    Parameters:
    - data: 2D list representing CSV rows.
    - year: Year to assume if it's missing in the date field.
    - column: Which column is the date column. By default, the first column (index 0).

    This one is a chatgpt modified version of fill_date_column to fix date format issues

    Accepts multiple formats like '8/24', '8/24/24', '8/24/2024'.
    """
    header = data[0]
    rows = data[1:]

    date_formats = [
        "%m/%d/%Y",       # ex: 8/24/2024
        "%m/%d/%y",       # ex: 8/24/24
        "%m/%d",          # ex: 8/24 — assume the given year
    ]

    current_date_str = None
    filled_rows = []

    for row in rows:
        raw_date = row[column].strip()

        if raw_date:
            parsed = None
            for fmt in date_formats:
                try:
                    if fmt == "%m/%d":
                        parsed = datetime.strptime(f"{raw_date}/{year}", "%m/%d/%Y")
                    else:
                        parsed = datetime.strptime(raw_date, fmt)
                    
                    #🩹 Fix bad year entries like 2013 or 2014 → 2023 or 2024
                    if parsed.year in {2013, 2014, 2015, 2016}:
                        corrected_year = (year // 10) * 10 + (parsed.year % 10)
                        parsed = parsed.replace(year=corrected_year)
                        
                    break
                except ValueError:
                    continue
            if parsed is None:
                # raise ValueError(f"Unrecognized date format: '{raw_date}'")
                print(f"Unrecognized date format: '{raw_date}', skipping row.")
                #dont want to raise an error, it will be removed in the next step anyways
                #remove_bad_rows runs after this function does
                continue
            current_date_str = parsed.strftime("%Y-%m-%d")
        elif current_date_str:
            # fill down
            pass
        else:
            raise ValueError("Missing date and nothing to fill down from.")

        row[column] = current_date_str
        filled_rows.append(row)

    return [header] + filled_rows

def remove_bad_rows(data: list[list[str]], filepath:str) -> list[list[str]]:
    """
    Removes rows with missing critical columns and returns good rows.

    filepath (str): the file to save the bad rows to.
    
    Note: Don't save these rows to clean_data folder, save them to raw_data
    Because they are likely not anonymized by this step in the process

    This is "step 3" in the original parsing
    """
    header = data[0]
    rows = data[1:]

    # Find indices for critical columns
    try:
        # game_index = header.index("Game")
        time_in_index = header.index("Time In")
        time_out_index = header.index("Time Out")
    except ValueError as e:
        raise ValueError("One or more required columns ('Game', 'Time In', 'Time Out') are missing.") from e

    good_rows = [header]
    bad_rows = [header]
    
    for row in rows:
        # Check if critical columns are non-empty
        if row[time_in_index].strip() and row[time_out_index].strip():
            good_rows.append(row)
        else:
            bad_rows.append(row)

    # Save bad rows separately
    save_csv(bad_rows, filepath)
    print("Bad rows saved to:", filepath)
    return good_rows


def anonymize_rows(data):
    """
    Replaces 'Name' and 'ID' columns with a unique identifier.

    This is "step 4" in the original parsing
    """
    header = data[0]
    rows = data[1:]

    # Map to track unique IDs
    unique_id_map = {}
    next_unique_id = 1

    new_header = [header[0]] + ["Unique ID"] + header[3:]  # Replace Name and ID
    anonymized_rows = []

    for row in rows:
        name = row[1]
        id_ = row[2]
        key = (name.strip(), id_.strip())

        if key not in unique_id_map:
            unique_id_map[key] = next_unique_id
            next_unique_id += 1

        # Replace Name and ID with Unique ID
        anonymized_row = [row[0]] + [unique_id_map[key]] + row[3:]
        anonymized_rows.append(anonymized_row)

    return [new_header] + anonymized_rows


#helper function for the next two functions
def is_valid_time(time_str: str) -> bool:
        """Checks if the given time string is in the valid HH:MM format."""
        try:
            parts = time_str.split(":")
            if len(parts) != 2:
                return False
            hour, minute = map(int, parts)
            return 0 <= hour < 24 and 0 <= minute < 60
        except ValueError:
            return False


def check_invalid_times(data: list[list[str]]) -> None:
    """
    Prints all invalid times. Doesn't modify anything, just checks for bad inputs.

    This was "step 5a" in the original parsing.
    """
    header = data[0]  # Header row
    rows = data[1:]  # Data rows

    print("Rows with invalid time formats. These should be removed from the dataset:")
    for row_num, row in enumerate(rows, start=2):  # Starting row number at 2 (header + 1-based index)
        time_in = row[3].strip()  # Assuming "Time In" is the fourth column
        time_out = row[4].strip()  # Assuming "Time Out" is the fifth column

        if not is_valid_time(time_in) or not is_valid_time(time_out):
            print(f"Row {row_num}: {row}")



def fix_time_disparity(data: list[list[str]]) -> list[list[str]]:
    """
    Fixes time disparity by converting 'Time In' and 'Time Out' to 24-hour military format,
    determining AM/PM based on context.

    time_in_index (int): which column is Time In
    time_out_index (int): which column is Time Out
    (be cautious of off-one errors!)

    This is "step 5b" in the original parsing
    """
    header = data[0]
    rows = data[1:]

    # Find indices for "Time In" and "Time Out" columns
    try:
        time_in_index = header.index("Time In")
        time_out_index = header.index("Time Out")
    except ValueError as e:
        raise ValueError("Required columns 'Time In' or 'Time Out' are missing.") from e

    is_it_afternoon_yet = False  # Initialize afternoon tracking flag
    previous_date = None  # Track date to reset the afternoon flag when the date changes

    adjusted_rows = []
    for row in rows:
        date = row[0]  # Assuming the date is in the first column
        time_in = row[time_in_index].strip()
        time_out = row[time_out_index].strip()

        # Reset the afternoon flag if it's a new day
        if date != previous_date:
            is_it_afternoon_yet = False
            previous_date = date

        # Validate "Time In" and "Time Out"
        if not is_valid_time(time_in) or not is_valid_time(time_out):
            print(f"Invalid time at Row {rows.index(row) + 2}: Time In = '{time_in}', Time Out = '{time_out}'")
            continue  # Skip this row entirely if either time is invalid, don't add to adjusted_rows

        # Fix 'Time In'
        hour_in, minute_in = map(int, time_in.split(':'))
        if (1 <= hour_in <= 9) or is_it_afternoon_yet:  # Time in the afternoon
            is_it_afternoon_yet = True  # Update afternoon status
            hour_in = (hour_in + 12) % 24  # Convert to military time
        row[time_in_index] = f"{hour_in:02}:{minute_in:02}"

        # Fix 'Time Out'
        hour_out, minute_out = map(int, time_out.split(':'))
        if (13 <= hour_in <= 23) or is_it_afternoon_yet:  # Real military time now
            is_it_afternoon_yet = True  # Afternoon status already set
            hour_out = (hour_out + 12) % 24  # Convert to military time if necessary
        elif 1 <= hour_out <= 9:  # Special case for crossing the afternoon line
            hour_out = (hour_out + 12) % 24
        row[time_out_index] = f"{hour_out:02}:{minute_out:02}"

        # Append the adjusted row
        adjusted_rows.append(row)

    return [header] + adjusted_rows


def add_duration_column(data: list[list[str]]) -> list[list[str]]:
    """
    Adds a 'Duration (minutes)' column based on 'Time In' and 'Time Out'.

    This is "step 6" in the original parsing
    """
    from datetime import datetime

    def calculate_duration_in_minutes(start_time: str, end_time: str) -> int:
        fmt = "%H:%M"
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)
        duration = (end - start).total_seconds() / 60
        return int(duration)

    header = data[0]
    rows = data[1:]

    # Find indices for "Time In" and "Time Out" columns
    try:
        time_in_index = header.index("Time In")
        time_out_index = header.index("Time Out")
    except ValueError as e:
        raise ValueError("Required columns 'Time In' or 'Time Out' are missing.") from e

    # Add the new column to the header
    updated_header = header + ["Duration (minutes)"]
    updated_rows = []

    for row in rows:
        if row[time_in_index].strip() and row[time_out_index].strip():  # Ensure valid times exist
            try:
                duration = calculate_duration_in_minutes(row[time_in_index], row[time_out_index])
                row.append(duration)
            except ValueError:
                # Handle invalid time format gracefully
                row.append(0)
        else:
            row.append(0)  # Default to 0 if times are missing
        updated_rows.append(row)

    return [updated_header] + updated_rows




def fill_game_column(data: list[list[str]]) -> list[list[str]]:
    """
    Fills empty cells in the 'Game' column with 'Unspecified'.

    Used for the video game data.
    """
    header = data[0]
    rows = data[1:]

    # Find the index of the "Game" column
    try:
        game_index = header.index("Game")
    except ValueError as e:
        raise ValueError("Required column 'Game' is missing.") from e

    # Process each row and update empty "Game" cells
    updated_rows = []
    for row in rows:
        if not row[game_index].strip():  # Check if the "Game" cell is empty
            row[game_index] = "Unspecified"
        updated_rows.append(row)

    return [header] + updated_rows




def fill_table_numbers(data: list[list[str]]) -> list[list[str]]:
    """
    Fills missing table numbers for specific table games based on predefined rules.
    Logs missing table numbers for 'Pool' as a special case.

    Used for the table game data.
    """
    # Define mapping of table games to default table numbers
    table_game_to_table_number = {
        "Air Hockey": "4",
        "Foosball": "5",
        "Shuffleboard": "6",
    }

    header = data[0]
    rows = data[1:]

    # Find indices for the relevant columns
    try:
        table_game_index = header.index("Table Game")
        table_number_index = header.index("Pool Table #")
    except ValueError as e:
        raise ValueError("Required columns 'Table Game' or 'Table #' are missing.") from e

    updated_rows = []
    for row_num, row in enumerate(rows, start=2):  # Start counting from 2 to account for the header
        table_game = row[table_game_index].strip()
        table_number = row[table_number_index].strip()

        # Fill missing table numbers based on game type
        if not table_number:
            if table_game in table_game_to_table_number:
                row[table_number_index] = table_game_to_table_number[table_game]
            elif table_game == "Pool":
                print(f"Missing Pool table number at Row {row_num}")
                row[table_number_index] = "0"  # Default to 0 for Pool
        updated_rows.append(row)

    return [header] + updated_rows




def fill_game_by_pool_table_number(data: list[list[str]]) -> list[list[str]]:
    """
    If the "Table Game" column is empty but the "Pool Table #" column has a value,
    then set the "Table Game" to "Pool".

    There was one row where this change was needed, which means it could happen again!
    """
    header = data[0]
    rows = data[1:]

    # Find indices for the relevant columns
    try:
        table_game_index = header.index("Table Game")
        pool_table_index = header.index("Pool Table #")
    except ValueError as e:
        raise ValueError("Required columns 'Table Game' or 'Pool Table #' are missing.") from e

    updated_rows = []
    for row in rows:
        table_game = row[table_game_index].strip()
        pool_table = row[pool_table_index].strip()

        # Check if "Table Game" is empty and "Pool Table #" has a valid value
        if not table_game and pool_table in {"1", "2", "3"}:
            row[table_game_index] = "Pool"

        updated_rows.append(row)

    return [header] + updated_rows


def fix_time_disparity_occupancy(data: list[list[str]]) -> list[list[str]]:
    """
    Fixes time disparity for the "Time" column in the Occupancy table by converting
    times to 24-hour military format, determining AM/PM based on context.

    This is a custom version for occupancy tables with only a "Time" column.
    """
    header = data[0]
    rows = data[1:]

    # Find the index of the "Time" column
    try:
        time_index = header.index("Time")
    except ValueError as e:
        raise ValueError("Required column 'Time' is missing.") from e

    is_it_afternoon_yet = False  # Initialize afternoon tracking flag
    previous_date = None  # Track date to reset the afternoon flag when the date changes

    adjusted_rows = []
    for row in rows:
        date = row[0]  # Assuming the date is in the first column
        time = row[time_index].strip()

        # Reset the afternoon flag if it's a new day
        if date != previous_date:
            is_it_afternoon_yet = False
            previous_date = date

        # Validate "Time"
        if not is_valid_time(time):
            print(f"Invalid time at Row {rows.index(row) + 2}: Time = '{time}'")
            continue  # Skip this row entirely if the time is invalid

        # Fix "Time"
        hour, minute = map(int, time.split(':'))
        if (1 <= hour <= 9) or is_it_afternoon_yet:  # Time in the afternoon
            is_it_afternoon_yet = True  # Update afternoon status
            hour = (hour + 12) % 24  # Convert to military time
        row[time_index] = f"{hour:02}:{minute:02}"

        # Append the adjusted row
        adjusted_rows.append(row)

    return [header] + adjusted_rows

from typing import List

def remove_bad_rows_occupancy(data: List[List[str]], filepath: str) -> List[List[str]]:
    """
    Removes rows with ANY missing values in the occupancy table and saves the bad rows.

    filepath (str): the file to save the bad rows to.
    """
    header = data[0]
    rows = data[1:]

    good_rows = [header]
    bad_rows = [header]

    for row in rows:
        if all(cell.strip() for cell in row):  # Check if all values are non-empty
            good_rows.append(row)
        else:
            bad_rows.append(row)

    # Save bad rows separately
    save_csv(bad_rows, filepath)
    print(f"Bad rows saved to: {filepath}")

    return good_rows



def is_valid_am_pm_time(time_str: str) -> bool:
    """
    Checks if the given time string is in a valid 'HH:MM AM/PM' format.
    """
    try:
        import re
        pattern = r"^(0?[1-9]|1[0-2]):[0-5][0-9]\s?(AM|PM)$"  # Regex for HH:MM AM/PM
        return bool(re.match(pattern, time_str.strip().upper()))
    except Exception:
        return False


def flag_out_of_range_am_pm_times(data: list[list[str]]) -> None:
    """
    Prints any time between 1:00 AM and 9:00 AM, flagging them as possibly incorrect.
    """
    from datetime import datetime

    header = data[0]
    rows = data[1:]

    # Find columns: "Time In", "Time Out", or "Time"
    time_columns = [col for col in ["Time In", "Time Out", "Time"] if col in header]
    if not time_columns:
        print("No valid time columns ('Time In', 'Time Out', 'Time') found.")
        return

    print("Flagged rows with times between 1:00 AM and 9:00 AM:")
    for row_num, row in enumerate(rows, start=2):
        for col in time_columns:
            time = row[header.index(col)].strip()
            if is_valid_am_pm_time(time):
                # Parse time into a datetime object
                dt = datetime.strptime(time, "%I:%M %p")
                if 1 <= dt.hour < 9:  # 1 AM to 9 AM
                    print(f"Row {row_num}: {col} = '{time}'")


def convert_am_pm_times_to_military(data: list[list[str]]) -> list[list[str]]:
    """
    Converts 'Time', 'Time In', and 'Time Out' columns to military (24-hour) format.
    For Fall 2024 onwards, the AM/PM disparity is no longer present.
    """
    from datetime import datetime

    header = data[0]
    rows = data[1:]

    # Find columns: "Time In", "Time Out", or "Time"
    time_columns = [col for col in ["Time In", "Time Out", "Time"] if col in header]
    if not time_columns:
        raise ValueError("No valid time columns ('Time In', 'Time Out', 'Time') found.")

    adjusted_rows = []
    for row in rows:
        new_row = row.copy()
        for col in time_columns:
            col_index = header.index(col)
            time = new_row[col_index].strip()

            # Convert only if valid
            if is_valid_am_pm_time(time):
                dt = datetime.strptime(time, "%I:%M %p")  # Parse as AM/PM
                new_row[col_index] = dt.strftime("%H:%M")  # Format to military time
            else:
                print(f"Invalid time skipped at Row {rows.index(row) + 2}: {time}")
        adjusted_rows.append(new_row)

    return [header] + adjusted_rows
