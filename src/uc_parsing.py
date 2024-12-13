import csv

#helper functions for reading and writing to csv
def read_csv(file_path):
    with open(file_path, mode='r', newline='') as infile:
        return list(csv.reader(infile))

def save_csv(data, file_path):
    with open(file_path, mode='w', newline='') as outfile:
        writer = csv.writer(outfile)
        writer.writerows(data)


def clean_board_games(raw_filepath,
                      bad_filepath,
                      clean_filepath,
                      last_real_column_index = 6
                     ):
    """
    Runs all of the parsing steps

    Filepath inputs are most likely:
        "../raw_data/board_games_raw.csv",
        "../raw_data/f23_board_games_bad_rows.csv",
        "../clean_data/f23_board_games_cleaned.csv"
    
    last_real_column_index (int): I'll think of a better name later...
    All of the spreadsheets tend to have empty/ghost columns at the end.
    This parameter specifies how many columns to keep.
    Columns after this are removed.
    """
    data = read_csv(raw_filepath)

    print("Parsing CSV at:", raw_filepath)

    data = resolve_board_game_notes_column(data)
    data = remove_empty_columns(data, last_real_column_index)
    data = fill_date_column(data)
    data = remove_bad_rows(data, bad_filepath)
    data = anonymize_rows(data)
    check_invalid_times(data)
    data = fix_time_disparity(data)
    data = add_duration_column(data)

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

    good_rows = [header]
    bad_rows = [header]
    for row in rows:
        # Assume columns 3-5 must not be empty
        if row[3].strip() and row[4].strip() and row[5].strip():
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


def check_invalid_times(data: list[list[str]]) -> None:
    """
    Prints all invalid times. Doesn't modify anything, just checks for bad inputs.

    This was "step 5a" in the original parsing.
    """
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

    header = data[0]  # Header row
    rows = data[1:]  # Data rows

    print("Rows with invalid time formats:")
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

        # Fix 'Time In' first
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

    def calculate_duration_in_minutes(start_time, end_time):
        fmt = "%H:%M"
        start = datetime.strptime(start_time, fmt)
        end = datetime.strptime(end_time, fmt)
        duration = (end - start).total_seconds() / 60
        return int(duration)

    header = data[0] + ["Duration (minutes)"]
    rows = data[1:]

    updated_rows = []
    for row in rows:
        if row[3].strip() and row[4].strip():  # Ensure valid times exist
            duration = calculate_duration_in_minutes(row[3], row[4])
            row.append(duration)
        else:
            row.append(0)  # Default to 0 if times are missing
        updated_rows.append(row)

    return [header] + updated_rows
