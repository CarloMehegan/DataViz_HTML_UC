import csv

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
'''

#helper functions for reading and writing to csv
def read_csv(file_path):
    with open(file_path, mode='r', newline='') as infile:
        return list(csv.reader(infile))

def save_csv(data, file_path):
    with open(file_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)

#main function to call to clean a file
def clean_games(raw_filepath,
                bad_filepath,
                clean_filepath,
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
    data = fill_date_column(data)
    data = remove_bad_rows(data, bad_filepath)
    data = anonymize_rows(data)
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
        if row[game_index].strip().lower() == "other":  # Check if 'Game' column contains 'Other'
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

def remove_bad_rows(data: list[list[str]], filepath:str) -> list[list[str]]:
    """
    Removes rows with missing critical columns and returns good rows.

    filepath (str): the file to save the bad rows to.
    NOTE: Don't save these rows to clean_data folder, save them to raw_data
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
