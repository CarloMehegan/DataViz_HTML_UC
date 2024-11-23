to do

- [x] add a readme

- [ ] add parsing code to repo and explain it in the readme

    - [ ] get parsing script working on fall 23 data

    - [ ] stress test parsing script using spring 24 data

    - [ ] automate parsing script for ongoing fall 24 data

- [x] remove extraneous html files (and other files)

- [ ] add andrew's sheets to csv script and explain it in the readme

- [ ] explain how to use the parsed data to create new viz, in the readme

- [ ] add new viz and update pages

- [ ] patch together sheets to csv to parsed csv to updated graphs workflow

- [ ] look into automating the workflow (heroku scheduling?)

- [ ] make the pages nice, add buttons and things, new pages for diff semesters,...

---

# Visualizing Union Central

Contributors: Carlo Mehegan, David Cho, Violet Shi, Andrew Choi

### Project goals

...

### What the data looks like
Here is an excerpt from the occupancy data. Time between occupancy recordings varies, from ten minutes to an hour. Occupancy is typically taken every 20-30 minutes. There are **2441 occupancy records**.

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

---
Table Game Data is collected in another table. Names and IDs have been removed and replaced with unique identifiers using a Python script. The date in the first column is only recorded for the first entry of each day, which must be accounted for when parsing. There are **3,598 rental records** for table games.

| Date    | Game       | In    | Out   | Table # |
|---------|------------|-------|-------|---------|
| 8/25    | Pool       | 12:14 | 12:25 | 1       |
|         | Foosball   | 12:14 | 12:30 |         |
|         | Pool       | 12:41 | 12:55 | 3       |
|         | Pool       | 12:58 | 1:07  | 2       |
|         | Pool       | 1:02  | 1:36  | 3       |
|         | Pool       | 1:09  | 1:20  | 3       |
|         | Pool       | 1:12  | 1:18  | 1       |

---

### Video Game Data
Video Game Data is collected in another table. Names and IDs have been removed. There are **448 rental records** for video games.

| Date | Console | Game             | Controllers | In    | Out   |
|------|---------|------------------|-------------|-------|-------|
| 9/2  | Xbox    | Minecraft        | 1           | 12:23 | 1:15  |
|      | Wii     | Mario Party 8    | 4           | 1:37  | 2:00  |
|      | Wii     | Mario Kart       | 2           | 2:55  | 5:02  |
|      | Xbox    | Minecraft        | 2           | 3:45  | 5:00  |
|      | Wii     | Splatoon         | 1           | 5:15  | 5:45  |
|      | Xbox    | Forza Horizon 5  | 1           | 7:02  | 9:44  |

---
Board Game Data is collected in another table. Names and IDs have been removed. The "Game" column is a dropdown containing only the nine most popular board games. This was changed in later semesters, but for this Fall 2023 data, discrepancies in the "Game" and "Notes" columns need to be considered. There are **113 rental records** for board games.

| Date  | Game                  | In    | Out   | Notes            |
|-------|-----------------------|-------|-------|------------------|
| 9/9   | Other (specify in Notes) | 7:14  | 8:08  | Chess            |
|       | Other (specify in Notes) | 9:12  | 9:31  | Set              |
| 9/10  | Other (specify in Notes) | 6:40  | 7:45  | Taboo            |
| 9/15  | Deck of Cards         | 6:31  | 6:34  |                  |
|       | Deck of Cards         | 7:53  | 8:08  |                  |
| 9/19  | Uno                   | 7:18  | 7:55  |                  |



### Google Sheets to CSV

TODO andrew


### Cleaning and parsing the data

TODO carlo


### Creating and updating visualizations

...
