# Visualizing Union Central

View the site live here: [https://carlomehegan.github.io/DataViz_HTML_UC/](https://carlomehegan.github.io/DataViz_HTML_UC/)

Contributors: Carlo Mehegan, David Cho, Violet Shi, Andrew Choi

## 🎯 Project goals

One of our group members works at Union Central, the games room in Sadler. During shifts, employees log occupancy and rentals. In a previous project for DATA303: Data Visualization, the UC Fall 2023 rental data was cleansed and analyzed, with the results and visualizations hosted on a static Github Pages site ([https://carlomehegan.github.io/DataViz_HTML_UC/](https://carlomehegan.github.io/DataViz_HTML_UC/)).

Our goal for the next phase of this project, for DATA440-6: Automations and Workflows, is to make it easier to expand this project with new data.

There are three parts we have highlighted for optimization:

1. Taking the data from Union Central's Google Sheets tables and turning them into raw CSVs we can work with
2. Cleansing the CSVs (removing blank lines, fixing errors, anonymizing data)
3. Remaking the site's visualizations to reflect new data

## 0. Structure of this repository

The `src` folder contains Python scripts used to collect, parse, and visualize data. You can find parsed and anonymized versions of the data in the `clean_data` folder. The `resources` folder contains assets like images, stylesheets, and Plotly files. The HTML files for the sites' pages are located in the main directory. Our DATA440-6 Project Writeup is located in the `project_proposal_writeup` folder.

## I. 🔍 Obtaining the data

The data is collected from Union Central's rental spreadsheet, recorded in Google Sheets by game attendants as rentals come in. The raw data is private, as it contains names and IDs of students, but cleaned and anonymized versions of the datasets are available for viewing in the `clean_data` folder.

### What does the data look like?

There are four tables: Occupancy, Table games, Video games, and Board games.

Here is an excerpt from the **occupancy data**. Time between occupancy recordings varies, from ten minutes to an hour. Occupancy is typically taken every 20-30 minutes. There are **2441 occupancy records**. See the cleaned version of the Fall 2023 occupancy data in [clean_data/f24_occupancy_clean.csv](clean_data/f24_occupancy_clean.csv), and an excerpt below.

| Day     | Date       | Headcount | Time of Record |
|---------|------------|-----------|----------------|
| Friday  | 8/25/2023  | 3         | 7:30           |
| Friday  | 8/25/2023  | 0         | 7:50           |
| Friday  | 8/25/2023  | 2         | 8:14           |
| Friday  | 8/25/2023  | 5         | 8:39           |
| Friday  | 8/25/2023  | 14        | 9:11           |
| Friday  | 8/25/2023  | 9         | 9:25           |
| Friday  | 8/25/2023  | 13        | 9:33           |
| Friday  | 8/25/2023  | 12        | 9:52           |

**Table Game Data** is collected in another table. Names and IDs have been removed and replaced with unique identifiers using a Python script. The date in the first column is only recorded for the first entry of each day, which must be accounted for when parsing. There are **3,598 rental records** for table games. See the cleaned version of the Fall 2023 table game data in [clean_data/f24_table_games_clean.csv](clean_data/f24_table_games_clean.csv), and an excerpt below.

| Date    | Game       | In    | Out   | Table # |
|---------|------------|-------|-------|---------|
| 8/25    | Pool       | 12:14 | 12:25 | 1       |
|         | Foosball   | 12:14 | 12:30 |         |
|         | Pool       | 12:41 | 12:55 | 3       |
|         | Pool       | 12:58 | 1:07  | 2       |
|         | Pool       | 1:02  | 1:36  | 3       |
|         | Pool       | 1:09  | 1:20  | 3       |
|         | Pool       | 1:12  | 1:18  | 1       |

**Video Game Data** is collected in another table. Names and IDs have been removed. There are **448 rental records** for video games. See the cleaned version of the Fall 2023 video game data in [clean_data/f24_video_games_clean.csv](clean_data/f24_video_games_clean.csv), and an excerpt below.

| Date | Console | Game             | Controllers | In    | Out   |
|------|---------|------------------|-------------|-------|-------|
| 9/2  | Xbox    | Minecraft        | 1           | 12:23 | 1:15  |
|      | Wii     | Mario Party 8    | 4           | 1:37  | 2:00  |
|      | Wii     | Mario Kart       | 2           | 2:55  | 5:02  |
|      | Xbox    | Minecraft        | 2           | 3:45  | 5:00  |
|      | Wii     | Splatoon         | 1           | 5:15  | 5:45  |
|      | Xbox    | Forza Horizon 5  | 1           | 7:02  | 9:44  |

**Board Game Data** is collected in another table. Names and IDs have been removed. The "Game" column is a dropdown containing only the nine most popular board games. This was changed in later semesters, but for this Fall 2023 data, discrepancies in the "Game" and "Notes" columns need to be considered. There are **113 rental records** for board games. See the cleaned version of the Fall 2023 board game data in [clean_data/f24_board_games_clean.csv](clean_data/f24_board_games_clean.csv), and an excerpt below.

| Date  | Game                  | In    | Out   | Notes            |
|-------|-----------------------|-------|-------|------------------|
| 9/9   | Other (specify in Notes) | 7:14  | 8:08  | Chess            |
|       | Other (specify in Notes) | 9:12  | 9:31  | Set              |
| 9/10  | Other (specify in Notes) | 6:40  | 7:45  | Taboo            |
| 9/15  | Deck of Cards         | 6:31  | 6:34  |                  |
|       | Deck of Cards         | 7:53  | 8:08  |                  |
| 9/19  | Uno                   | 7:18  | 7:55  |                  |


### Google Sheets to CSV Setup

Rental data is recorded every day by employees at Union Central. We would like to collect this data as often as possible to keep the site's visualizations for the current semester up to date. To do this, we have created a script that works with Google Sheets' API to pull the data when executed. This can be found in [src/sheets_to_csv.py](src/sheets_to_csv.py).

To interact with Google Sheets' API you'll need to setup the Google Sheets API properly as well as authenticate your app to access the data. A step-by-step guide to help with configuring the Google Sheets API for your environment is posted right below. If there are any issues you can also refer to this documentation: https://developers.google.com/sheets/api/quickstart/python

**Prerequisites**
- Python 3.10.7 or greater
- The pip package management tool
- A Google Cloud project (you’ll need to set up a project in the Google Cloud Console)
- A Google Account

**Enable the Google Sheets API**
1. Go to the Google Cloud Console
2. Create a new project or select an existing one.
3. Navigate to APIs & Services > Library and search for Google Sheets API
4. Click Enable to activate the Google Sheets API for your project

**Configure OAuth Consent Screen**
1. Go to APIs & Services > OAuth consent screen.
2. Select User type (our case we chose External so anyone with a Google Account can test this).
3. Complete the registration form by first adding the name of the project and making sure to fill out the support email and the developer contact information with the same email address
4. Add scopes (permission) by clicking on "add or remove scopes" and choosing Google Sheets API (/auth/spreadsheets)
5. Add yourself and others as Test Users

**Create OAuth 2.0 Credentials**
1. In the Google Cloud Console, go to Credentials under APIs & Services.
2. Click Create Credentials > OAuth 2.0 Client ID.
3. Choose Application type > Desktop app (call this anything you want).
4. Name the credential (e.g., “Google Sheets API”).
5. Click Create, then download the credentials.json file and save it to your project directory.

**Install Required Python Libraries**
In order to interact with Google Sheets API, there are 3 necessary libraries that need to be installed by running the following command in your terminal:
```python
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

**Authentication and Token Setup**
1. When you first run the application, it will prompt you to authenticate using your Google Account.
2. Follow the prompts to sign in and grant permission for your app to access the Google Sheets data.
3. After successful authentication, the app will save the credentials in a file called token.json in your project directory. This token allows the app to access the Google Sheets API without requiring re-authentication in future runs.

You should now be ready to run the following script:
```python
python sheets_to_csv.py
```

## II. 🧹 Cleaning and parsing the data

As listed above, there are four datasets to work with. Table games, video games, and board games are all fairly similar, with occupancy being the odd one out.

For table games, video games, and board games, data cleansing follows this process:

1. **Remove empty columns** or extraneous columns that showed up when converting from Sheets to CSV
2. **Fill the date column**. The date column is typically only filled out for the first rental of the day, to mark where one day ends and the next day begins. For our purposes we want to "fill down" so that each rental has its proper date.
3. Identify, try to amend, and finally, **remove any bad rows**. A "bad row" has empty cells or does not match the typical format of a rental. Optionally, move bad rows to a separate CSV instead of dropping them, in case there are patterns in these "bad rows" that we can try to accommodate for. For example, if only the student ID is missing from the rental, we do not need to count it as a bad row, since we anonymize the data anyways.
4. **Anonymize the data**. Either remove all names and IDs, or give each person a new, unique identifier to preserve the relationship between rentals. This relationship data is not currently utilized, but may be valuable for future analysis.
5. (For the table games dataset) **Fill table number column**. The "table number" column contains 1, 2, or 3 to denote which of the three pool tables is in use. This helps employees track which renter is at which table. The column is empty for other games, like air hockey. To make sure nothing goes wrong later down the line, we fill all cells in this column, even if the rental wasn't for a pool table. Currently, 0 = Pool table rental with no recorded table number, 1-3 = Respective pool table, 4 = Air Hockey, 5 = Foosball, 6 = Shuffleboard.
6. **Ensure all times are formatted correctly** in the Time In and Time Out columns, in preparation for step 7.
7. **Convert all times to military time**. The recorded times have AM/PM ambiguity, so it's unclear if a rental was made at 10:15am or 10:15pm. To fix this, we convert all times to military time, assuming that rentals before noon each day are AM and rentals after noon each day are PM.
8. **Add a "Durations" column**. This takes our nice, new military times, calculates the length of the rental in minutes, and appends it to the end of each row. Duration is used for a lot of analysis, so it's worth calculating here instead of doing it multiple times later.
9. For board games, we also fix the "Other" discrepancy mentioned in the previous section by merging the "Game" and "Notes" columns.

Cleaning the occupancy data is much simpler. We remove bad rows and we convert everything to military time using the same method described in step 7.

The cleansing script can be found in `src/uc_parsing.py`. This script is able to parse all four types of rental data we are analyzing.

## III. 📈 Creating visualizations with Plotly

All of the visualizations on the site ([https://carlomehegan.github.io/DataViz_HTML_UC/](https://carlomehegan.github.io/DataViz_HTML_UC/)) are created with Plotly. Plotly lets us generate static, HTML visualizations that can be embedded on the site. And you can interact with them!

Like the parsing scripts, our Plotly scripts are a bit scattered between different Jupyter notebooks. We created a script that rebuilds all of these Plotly graphs, in order to keep the graphs on the site up to date.

## IV. 🤖 Automation

Once we have the previous three steps completed, we would like to create some kind of automatic routine that runs all three parts and keeps the website updated. We've looked into Heroku as a platform for this, and plan to implement this for the Spring 2025 semester.

## V. 🌐 Website

Currently, the website shows Fall 2023, Spring 2024, and Fall 2024 data. You can navigate between semesters using the top navigation bar and navigate between types of rental data using the map or the side buttons.
