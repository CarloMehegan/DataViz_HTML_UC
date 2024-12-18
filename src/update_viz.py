import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import Counter

"""
This script contains a function to make each of the visualizations on the site.
Each function takes a filepath as input and a name as input to be prefixed to the Plotly file name.

These scripts were originally written by Carlo, Violet and David for DATA303
They have been refactored into standalone functions using ChatGPT

TODO
lots of repeating, copy pasted code that could be fixed with helper functions / proper globals
however it is nice that each of these functions works standalone
with continued development / introduction of a lot more viz, it might be best to rethink this
"""

def run_all_visualizations(semester_name: str = "f23", output_path: str = "../resources/viz/f23") -> None:
    """
    Runs all visualizations for video games, table games, board games, and occupancy.
    This function assumes all of the data is in ../clean_data/
    
    semester_name should be "f23" or "s24" or "f24" etc.

    since we put our viz in a different folder, you can tweak the output_path in this function too
    this is actually just the semester name, which is why it's "../resources/viz/f23" and not "../resources/viz/"
    """
    print("\nStarting All Visualizations...\n")

    run_video_game_visualizations("../clean_data/" + semester_name + "_video_games_cleaned.csv", output_path)
    run_table_game_visualizations("../clean_data/" + semester_name + "_table_games_cleaned.csv", output_path)
    run_board_game_visualizations("../clean_data/" + semester_name + "_board_games_cleaned.csv", output_path)
    run_occupancy_visualizations("../clean_data/" + semester_name + "_occupancy_cleaned.csv", output_path)

    print("All Visualizations Complete!")

def run_video_game_visualizations(filepath: str, semester_name: str = "") -> None:
    """
    Runs all video game-related visualizations.
    """
    print("\nRunning Video Game Visualizations...")
    _rental_duration_by_console(filepath, semester_name)
    _controllers_by_top_games(filepath, semester_name)
    _video_game_rentals_pie_chart(filepath, semester_name)
    print("Video Game Visualizations Complete!\n")


def run_table_game_visualizations(filepath: str, semester_name: str = "") -> None:
    """
    Runs all table game-related visualizations.
    """
    print("\nRunning Table Game Visualizations...")
    _pool_table_duration_by_table(filepath, semester_name)
    _table_game_rentals_pie_chart(filepath, semester_name)
    _table_game_duration_distributions(filepath, semester_name)
    print("Table Game Visualizations Complete!\n")


def run_board_game_visualizations(filepath: str, semester_name: str = "") -> None:
    """
    Runs all board game-related visualizations.
    """
    print("\nRunning Board Game Visualizations...")
    _board_game_duration_distribution(filepath, semester_name)
    _board_game_frequency_vs_duration(filepath, semester_name)
    print("Board Game Visualizations Complete!\n")


def run_occupancy_visualizations(filepath: str, semester_name: str = "") -> None:
    """
    Runs all occupancy-related visualizations.
    """
    print("\nRunning Occupancy Visualizations...")
    _weekly_occupancy_trend(filepath, semester_name)
    _occupancy_by_month_and_weekday(filepath, semester_name)
    print("Occupancy Visualizations Complete!\n")


def _rental_duration_by_console(filepath: str, semester_name: str = "") -> None:
    """
    Generates a visualization of rental duration by console,
    """
    # Load the CSV data
    data = pd.read_csv(filepath)

    # Clean the data: remove rows with missing or invalid durations
    data = data.dropna(subset=["Console", "Duration (minutes)"])  # Ensure required columns are not null
    data = data[data["Duration (minutes)"] > 0]  # Keep only positive durations

    # Define graph configurations
    xaxis_format = {
        'title': None,
        'tickmode': 'array',
    }
    yaxis_format = {
        'title': 'Duration (minutes)',
        'gridcolor': 'rgba(128, 128, 128, 0.4)',
    }
    FIG_SIZE = {'width': 600, 'height': 400}
    BASE_FORMAT = {}  # Define your BASE_FORMAT if applicable
    TITLE_FORMAT = {}  # Define your TITLE_FORMAT if applicable
    PLOT_COLOR = 'rgba(255,255,255,1)'  # Default background color
    PAPER_COLOR = 'rgba(255,255,255,1)'  # Default paper color

    # Create the strip plot
    fig = px.strip(
        **FIG_SIZE,
        data_frame=data,
        x='Console',
        y='Duration (minutes)',
        stripmode='overlay',
        title='Rental Duration by Console',  # Title is now generic
    )
    fig.update_traces(marker=dict(opacity=0.3))

    # Add a box plot trace
    box = go.Box(
        x=data['Console'],
        y=data['Duration (minutes)'],
        hoverinfo='skip',
        marker={'opacity': 0.5, 'color': 'green'},
    )
    fig.add_trace(box)

    # Update trace and layout
    fig.update_traces(marker={'color': 'blue'}, selector={'name': 'strip'})
    fig.update_layout(
        **BASE_FORMAT,
        **FIG_SIZE,
        xaxis=xaxis_format,
        yaxis=yaxis_format,
        title=TITLE_FORMAT,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        showlegend=False,
    )

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}video_duration_by_console.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")



def _controllers_by_top_games(filepath: str, semester_name: str = "") -> None:
    """
    Generates a bar chart of controllers rented for the top 5 most rented games.
    """
    # Load the CSV data
    data = pd.read_csv(filepath)

    # Clean and preprocess data
    # Convert '# of Controllers' to integers where possible, and label non-integer values as "Other"
    def parse_controllers(value):
        try:
            return int(value)
        except ValueError:
            return "Other"

    data['# of Controllers'] = data['# of Controllers'].apply(parse_controllers)

    # Count the frequency of rentals for each game
    game_counts = data.groupby(['Game', '# of Controllers']).size().reset_index(name='Frequency')

    # Get the top 5 most rented games
    top_games = (
        game_counts.groupby('Game')['Frequency']
        .sum()
        .sort_values(ascending=False)
        .head(5)
        .index
    )

    # Filter data for the top 5 games
    top_data = game_counts[game_counts['Game'].isin(top_games)]

    # Plot the data
    FIG_SIZE = {'width': 600, 'height': 400}
    BASE_FORMAT = {
        'font_color': 'black',
        'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}
    }

    fig = px.bar(
        **FIG_SIZE,
        data_frame=top_data,
        x='Game',
        y='Frequency',
        color='# of Controllers',
        title='Controllers Rented, for the top 5 titles',
        barmode="group",
        color_discrete_sequence=px.colors.sequential.Plasma_r
    )

    fig.update_traces(hovertemplate='Frequency = %{y}')
    fig.update_layout(
        **BASE_FORMAT,
        font_family='Droid Sans',
        title={'x': 0.5, 'xanchor': 'center', 'font_size': 22, 'y': 0.85}
    )
    fig.update_xaxes(title='')
    fig.update_layout(barmode='group')  # Change to side-by-side bars

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}controller_by_top_game.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")





def _video_game_rentals_pie_chart(filepath: str, semester_name: str = "") -> None:
    """
    Generates pie charts of video game rentals by console (Xbox and Wii).
    """
    # Load data
    data = pd.read_csv(filepath)

    # Initialize Counters to count occurrences of each video game for each console
    xbox_rentals = Counter(data.loc[data['Console'] == 'Xbox', 'Game'])
    wii_rentals = Counter(data.loc[data['Console'] == 'Wii', 'Game'])

    # Helper function to group "Other" games
    def process_counts(counter):
        final_counts = Counter()
        other_count = 0
        for game, count in counter.items():
            if count < 5:  # Games rented less than 5 times are grouped into "Other"
                other_count += count
            else:
                final_counts[game] = count
        if other_count > 0:
            final_counts['Other'] = other_count
        return final_counts

    # Process counts for Xbox and Wii
    xbox_final_counts = process_counts(xbox_rentals)
    wii_final_counts = process_counts(wii_rentals)

    # Create a subplot with 1 row and 2 columns for pie charts
    fig = make_subplots(
        rows=1, cols=2, specs=[[{'type': 'domain'}, {'type': 'domain'}]],
        subplot_titles=(f"Xbox Rentals ({sum(xbox_final_counts.values())} total)",
                        f"Wii Rentals ({sum(wii_final_counts.values())} total)")
    )

    # Add Xbox pie chart
    fig.add_trace(go.Pie(
        labels=list(xbox_final_counts.keys()), 
        values=list(xbox_final_counts.values()),
        text=[f"{game}<br>{count} rentals" for game, count in xbox_final_counts.items()],
        textinfo='text+percent',
        textfont=dict(size=15),
        textposition='inside'
    ), row=1, col=1)

    # Add Wii pie chart
    fig.add_trace(go.Pie(
        labels=list(wii_final_counts.keys()), 
        values=list(wii_final_counts.values()),
        text=[f"{game}<br>{count} rentals" for game, count in wii_final_counts.items()],
        textinfo='text+percent',
        textfont=dict(size=15),
        textposition='inside'
    ), row=1, col=2)

    # Update layout
    fig.update_layout(
        font_family='Droid Serif',
        font_color='black',
        hoverlabel=dict(font_color='white', bgcolor='black'),
        title_text='Video Game Rentals by Console',
        width=850,
        height=500,
        title_font_size=30,
        showlegend=False,
        margin=dict(l=20, r=20, t=140, b=20)
    )

    fig.add_annotation(
        text="The \"Other\" category combines games rented less than five times.",
        align='left',
        showarrow=False,
        xref='paper',
        yref='paper',
        x=0.026,
        y=1.19,
        font=dict(size=18)
    )

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}games_pie_chart_divided.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")



def _board_game_duration_distribution(filepath: str, semester_name: str = "") -> None:
    """
    Generates a histogram of board game usage durations.
    """
    # Load data
    data = pd.read_csv(filepath)

    # Clean and preprocess data: remove rows with invalid or missing durations
    data = data.dropna(subset=["Duration (minutes)"])  # Ensure no missing durations
    data = data[data["Duration (minutes)"] > 0]  # Keep only positive durations

    # Define configurations
    FIG_SIZE = {'width': 600, 'height': 400}
    TICK_SIZE = 16
    LABEL_SIZE = 18
    TITLE_SIZE = 22

    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'

    BASE_FORMAT = {'font_family': 'Droid Serif',
                   'font_color': 'black',
                   'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}
                  }

    AXIS_FORMAT = {'tickfont_size': TICK_SIZE,
                   'title_font_size': LABEL_SIZE
                  }

    TITLE_FORMAT = {'x': 0.5,
                    'xanchor': 'center',
                    'font_size': TITLE_SIZE,
                    'y': 0.85
                   }

    xaxis_format = {**AXIS_FORMAT,
                    'title': 'Duration (minutes)',
                    'tickmode': 'array',
                    'tickvals': list(range(0, int(data['Duration (minutes)'].max()), 25))
                   }

    yaxis_format = {**AXIS_FORMAT,
                    'title': '# of Checkouts',
                    'gridcolor': 'rgba(128, 128, 128, 0.5)'
                   }

    # Create the histogram
    fig = px.histogram(
        **FIG_SIZE,
        data_frame=data,
        x='Duration (minutes)',
        title='Board Game Usage Time Trend'
    )

    # Update layout
    fig.update_layout(
        **BASE_FORMAT,
        **FIG_SIZE,
        xaxis=xaxis_format,
        yaxis=yaxis_format,
        title=TITLE_FORMAT,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        bargap=0.1,
        showlegend=False
    )

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}board_game_duration_distribution.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")



def _board_game_frequency_vs_duration(filepath: str, semester_name: str = "") -> None:
    """
    Generates a scatter plot showing the frequency and average duration of each board game.
    """
    # Load data
    data = pd.read_csv(filepath)

    # Clean and preprocess data
    data = data.dropna(subset=["Game", "Duration (minutes)"])  # Remove rows with missing values
    data = data[data["Duration (minutes)"] > 0]  # Keep only positive durations

    # Calculate frequency and average duration per game
    aggregated_data = (
        data.groupby("Game")["Duration (minutes)"]
        .agg(Frequency="count", Average_Duration="mean")
        .reset_index()
    )

    # Define configurations
    FIG_SIZE = {'width': 600, 'height': 500}
    TICK_SIZE = 14
    LABEL_SIZE = 18
    TITLE_SIZE = 22

    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'

    BASE_FORMAT = {'font_family': 'Droid Serif',
                   'font_color': 'black',
                   'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}
                  }

    AXIS_FORMAT = {'tickfont_size': TICK_SIZE,
                   'title_font_size': LABEL_SIZE
                  }

    TITLE_FORMAT = {'x': 0.49,
                    'xanchor': 'center',
                    'font_size': TITLE_SIZE,
                    'y': 0.94
                   }

    xaxis_format = {**AXIS_FORMAT,
                    'title': 'Average Duration (minutes)'
                   }

    yaxis_format = {**AXIS_FORMAT,
                    'title': 'Frequency (log scale)',
                    'type': 'log',
                    'gridcolor': 'rgba(128, 128, 128, 0.5)'
                   }

    # Create scatter plot
    fig = px.scatter(
        width=FIG_SIZE['width'],
        height=FIG_SIZE['height'],
        data_frame=aggregated_data,
        x='Average_Duration',
        y='Frequency',
        color='Game',
        hover_name='Game',
        color_discrete_sequence=['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'magenta', 'yellow', 'lime', 'pink', 'teal', 'lavender', 'brown', 'grey', 'olive']
    )

    fig.update_traces(marker=dict(size=20))

    # Update layout
    fig.update_layout(
        **BASE_FORMAT,
        **FIG_SIZE,
        xaxis=xaxis_format,
        yaxis=yaxis_format,
        title={'text': 'Frequency and Average Duration of Each Game', **TITLE_FORMAT},
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        showlegend=True
    )

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}board_game_frequency_vs_avr_duration.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")



def _pool_table_duration_by_table(filepath: str, semester_name: str = "") -> None:
    """
    Generates a visualization of Pool Table rental durations by table number.
    """
    # Load data
    data = pd.read_csv(filepath)

    # Filter data for Pool games only
    pool_data = data[data["Table Game"] == "Pool"]

    # Add "Adjusted Duration" column (for log scale, add 1 to all durations if needed)
    pool_data = pool_data.copy()
    pool_data["Adjusted Duration"] = pool_data["Duration (minutes)"]

    # Define configurations
    FIG_SIZE = {'width': 800, 'height': 400}
    TICK_SIZE = 16
    LABEL_SIZE = 18
    TITLE_SIZE = 22

    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'

    BASE_FORMAT = {'font_family': 'Droid Serif',
                   'font_color': 'black',
                   'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}
                  }

    AXIS_FORMAT = {'tickfont_size': TICK_SIZE,
                   'title_font_size': LABEL_SIZE
                  }

    TITLE_FORMAT = {'x': 0.5,
                    'xanchor': 'center',
                    'font_size': TITLE_SIZE,
                    'y': 0.85
                   }

    xaxis_format = {**AXIS_FORMAT,
                    'title': None,
                    'tickmode': 'array',
                    'tickvals': pool_data['Pool Table #'].unique(),
                    'ticktext': ['Table {}'.format(num) for num in pool_data['Pool Table #'].unique()]
                   }

    yaxis_format = {**AXIS_FORMAT,
                    'title': 'Duration (log scale)',
                    'gridcolor': 'rgba(128, 128, 128, 0.4)'
                   }

    # Create the strip plot
    fig = px.strip(
        **FIG_SIZE,
        data_frame=pool_data,
        x='Pool Table #',
        y='Adjusted Duration',
        stripmode='overlay',
        title='Pool Table Rental Duration'
    )

    fig.update_traces(marker=dict(opacity=0.3))

    # Add a box plot trace
    box = go.Box(
        x=pool_data['Pool Table #'],
        y=pool_data['Adjusted Duration'],
        hoverinfo='skip',
        marker={'opacity': 0.5, 'color': 'green'}
    )

    fig.add_trace(box)

    # Update trace and layout
    fig.update_traces(marker={'color': 'blue'}, selector={'name': 'strip'})
    fig.update_layout(
        **BASE_FORMAT,
        **FIG_SIZE,
        xaxis=xaxis_format,
        yaxis=yaxis_format,
        title=TITLE_FORMAT,
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        showlegend=False
    )

    fig.update_yaxes(type='log')  # Set y-axis to log scale

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}pool_duration_by_table_number.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")


def _table_game_rentals_pie_chart(filepath: str, semester_name: str = "") -> None:
    """
    Generates a pie chart of table game rentals by game type.
    """
    # Load data
    data = pd.read_csv(filepath)

    # Aggregate the counts of each game
    game_counts = data['Table Game'].value_counts()

    # Creating custom text for each slice
    custom_text = [f"{game}<br>{count} rentals" for game, count in game_counts.items()]

    # Plotting the pie chart
    fig = go.Figure(data=[go.Pie(
        labels=game_counts.index, 
        values=game_counts.values,
        text=custom_text,  # Use custom text for each slice
        textinfo='text+percent',  # Display custom text and percent
        textfont=dict(size=15),  # Specify the text font size
    )])

    # Define configurations
    FIG_SIZE = {'width': 600, 'height': 400}
    TITLE_SIZE = 22

    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'

    BASE_FORMAT = {'font_family': 'Droid Serif',
                   'font_color': 'black',
                   'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}
                  }

    TITLE_FORMAT = {'x': 0.4,
                    'xanchor': 'center',
                    'font_size': TITLE_SIZE,
                    'y': 0.91
                   }

    # Update layout with provided formatting parameters
    fig.update_layout(
        **BASE_FORMAT,
        **FIG_SIZE,
        title={**TITLE_FORMAT, 'text': 'Table Game Rentals by Game Type'},
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        showlegend=False,
        margin=dict(l=20, r=20, t=100, b=20)  # Adjust margins if necessary
    )

    # Show the pie chart
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}table_games_pie_chart.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")





# def _table_game_duration_distributions(filepath: str, semester_name: str = "") -> None:
#     """
#     Generates histogram-like bar charts for Air Hockey, Foosball, and Shuffleboard.
#     Manually bins data into fixed 5-minute intervals (0-4, 5-9, ..., 125-129).
#     """
#     # Load data
#     data = pd.read_csv(filepath)

#     # Filter for the specific games
#     table_games = ["Air Hockey", "Foosball", "Shuffleboard"]

#     # Define bins: Fixed width of 5 minutes
#     bins = list(range(0, 130, 5))  # Bin edges: 0, 5, 10, ..., 125, 130
#     bin_labels = [f"{i}-{i+4}" for i in range(0, 125, 5)]  # Labels: 0-4, 5-9, ..., 125-129

#     # Visualization parameters
#     FIG_SIZE = {'width': 600, 'height': 400}
#     TICK_SIZE = 16
#     LABEL_SIZE = 18
#     TITLE_SIZE = 22

#     BASE_FORMAT = {'font_family': 'Droid Serif',
#                    'font_color': 'black',
#                    'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}}

#     AXIS_FORMAT = {'tickfont_size': TICK_SIZE, 'title_font_size': LABEL_SIZE}
#     TITLE_FORMAT = {'x': 0.5, 'xanchor': 'center', 'font_size': TITLE_SIZE, 'y': 0.85}

#     for game in table_games:
#         # Filter and copy data for the specific game
#         game_data = data[data["Table Game"] == game].copy()

#         # Bin the data using pd.cut
#         game_data["Duration Bin"] = pd.cut(
#             game_data["Duration (minutes)"], bins=bins, labels=bin_labels, include_lowest=True, right=False
#         )

#         # Aggregate counts for each bin
#         bin_counts = game_data["Duration Bin"].value_counts().sort_index()

#         # Convert to DataFrame for plotting
#         plot_data = pd.DataFrame({
#             "Duration Bin": bin_counts.index,
#             "# of Checkouts": bin_counts.values
#         })

#         # Create bar chart
#         fig = px.bar(
#             plot_data,
#             x="Duration Bin",
#             y="# of Checkouts",
#             title=f"{game} Usage Time Trend",
#             **FIG_SIZE
#         )

#         # Customize layout
#         fig.update_layout(
#             **BASE_FORMAT,
#             xaxis={
#                 **AXIS_FORMAT,
#                 'tickmode': 'array',
#                 'tickvals': [0, 25, 50, 75, 100, 125],  # Custom ticks
#                 'ticktext': ['0', '25', '50', '75', '100', '125'],  # Labels
#                 'title': {'text': 'Duration (minutes)', 'font_size': LABEL_SIZE}
#             },
#             yaxis={
#                 **AXIS_FORMAT,
#                 'gridcolor': 'rgba(128, 128, 128, 0.5)',
#                 'title': {'text': '# of Checkouts', 'font_size': LABEL_SIZE}
#             },
#             title=TITLE_FORMAT,
#             bargap=0.1,
#             plot_bgcolor="white",
#             paper_bgcolor="white",
#             showlegend=False
#         )

#         # Show and save the chart
#         fig.show()
#         filename_prefix = f"{semester_name}_" if semester_name else ""
#         output_filename = f"{filename_prefix}{game.lower().replace(' ', '_')}_usage_trend.html"
#         fig.write_html(output_filename)
#         print(f"Visualization saved as {output_filename}")


import pandas as pd
import plotly.express as px

def _table_game_duration_distributions(filepath: str, semester_name: str = "") -> None:
    """
    Generates THREE histogram visualizations for game duration distributions.
    """
    # Visualization parameters
    FIG_SIZE = {'width': 600, 'height': 400}
    TICK_SIZE = 16
    LABEL_SIZE = 18
    TITLE_SIZE = 22
    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'
    
    BASE_FORMAT = {
        'font_family': 'Droid Serif',
        'font_color': 'black',
        'hoverlabel': {
            'font_color': 'white',
            'bgcolor': 'black'
        }
    }
    
    AXIS_FORMAT = {
        'tickfont_size': TICK_SIZE,
        'title_font_size': LABEL_SIZE
    }
    
    TITLE_FORMAT = {
        'x': 0.5,
        'xanchor': 'center',
        'font_size': TITLE_SIZE,
        'y': 0.85
    }
    
    # Load data
    data = pd.read_csv(filepath)
    
    # List of games to process
    games = ['Air Hockey', 'Foosball', 'Shuffleboard']
    
    # Define consistent bin edges
    bin_edges = list(range(0, 130, 5))
    bin_labels = [f'{start}-{start+4}' for start in range(0, 125, 5)]
    
    for game in games:
        # Filter data for the specific game and create a copy
        game_data = data[data['Table Game'] == game].copy()
        
        # Bin the durations, filtering out outliers
        game_data.loc[:, 'Binned Duration'] = pd.cut(
            game_data['Duration (minutes)'], 
            bins=bin_edges, 
            labels=bin_labels, 
            right=False
        )
        
        # Count occurrences in each bin
        binned_counts = game_data['Binned Duration'].value_counts().sort_index()
        
        # Create DataFrame for plotting
        plot_data = pd.DataFrame({
            'Duration': binned_counts.index,
            'Count': binned_counts.values
        })
        
        # Create bar plot instead of histogram to have more control
        fig = px.bar(
            plot_data, 
            x='Duration', 
            y='Count',
            title=f'{game} Usage Time Trend',
            labels={'Duration': 'Duration (minutes)', 'Count': '# of Checkouts'}
        )
        
        # Customize layout
        fig.update_layout(
            **BASE_FORMAT,
            **FIG_SIZE,
            bargap=0.1,
            xaxis={
                **AXIS_FORMAT,
                'categoryorder': 'array',
                'categoryarray': bin_labels,
                'tickmode': 'array',
                'tickvals': ['0-4', '20-24', '45-49', '70-74', '95-99', '120-124'],
                'ticktext': ['0', '25', '50', '75', '100', '125'],
                'title': {'text': 'Duration (minutes)', 'font_size': LABEL_SIZE}
            },
            yaxis={
                **AXIS_FORMAT,
                'gridcolor': 'rgba(128, 128, 128, 0.5)',
                'title': {'text': '# of Checkouts', 'font_size': LABEL_SIZE}
            },
            title=TITLE_FORMAT,
            plot_bgcolor=PLOT_COLOR,
            paper_bgcolor=PAPER_COLOR,
            showlegend=False
        )
        
        # Generate filename
        filename_prefix = f"{semester_name}_" if semester_name else ""
        output_filename = f"{filename_prefix}{game.lower().replace(' ', '_')}_usage_trend.html"
        
        # Save and show figure
        fig.write_html(output_filename)
        print(f"Visualization saved as {output_filename}")
        
        # Optional: display the figure (comment out if not needed)
        fig.show()



def _weekly_occupancy_trend(filepath: str, semester_name: str = "") -> None:
    """
    Generates a bar chart showing the weekly trend of total occupancy.
    """
    # Load data
    data = pd.read_csv(filepath)

    # Aggregate total headcount by day of the week
    weekly_trend = data.groupby("Day")["Headcount"].sum()

    # Ensure the days are in the correct order
    day_order = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    weekly_trend = weekly_trend.reindex(day_order).fillna(0)

    # Create a bar trace
    trace = go.Bar(
        x=weekly_trend.index,  # Days of the week
        y=weekly_trend.values,  # Total occupancy per day
        marker=dict(color='rgb(26, 118, 255)'),  # Color of the bars
    )

    # Layout
    TITLE_SIZE = 22
    LABEL_SIZE = 18
    TICK_SIZE = 16
    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'
    BASE_FORMAT = {'font_family': 'Droid Serif', 'font_color': 'black'}

    layout = go.Layout(
        title={
            'text': 'Weekly Trend of Total Occupancy',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': TITLE_SIZE}
        },
        xaxis={
            'title': {
                'text': 'Day of the Week',
                'font': {'size': LABEL_SIZE}
            },
            'tickmode': 'array',
            'categoryorder': 'array',
            'categoryarray': day_order,
            'tickfont': {'size': TICK_SIZE}
        },
        yaxis={
            'title': {
                'text': 'Total Occupancy',
                'font': {'size': LABEL_SIZE}
            },
            'gridcolor': 'rgba(128, 128, 128, 0.4)',
            'tickfont': {'size': TICK_SIZE}
        },
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        font={
            'family': BASE_FORMAT['font_family'],
            'color': BASE_FORMAT['font_color']
        },
        width=600,
        height=400
    )

    # Create Figure object
    fig = go.Figure(data=[trace], layout=layout)

    # Show interactive plot
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}occupancy_by_weekday.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")



def _occupancy_by_month_and_weekday(filepath: str, semester_name: str = "") -> None:
    """
    Generates a grouped bar chart showing occupancy by weekday and month.
    """
    # Load data
    data = pd.read_csv(filepath)

    # Extract the month name from the Date column
    data['Month'] = pd.to_datetime(data['Date']).dt.strftime('%B')  # Converts to month names
    data['Day'] = pd.Categorical(data['Day'], categories=["Monday", "Tuesday", "Wednesday", 
                                                          "Thursday", "Friday", "Saturday", 
                                                          "Sunday"], ordered=True)

    # Aggregate headcount by Month and Day of the Week
    aggregated_data = data.groupby(['Month', 'Day'], observed=True)['Headcount'].sum().reset_index()

    # Define configurations
    FIG_SIZE = {'width': 600, 'height': 400}
    TICK_SIZE = 16
    LABEL_SIZE = 18
    TITLE_SIZE = 22
    PLOT_COLOR = 'white'
    PAPER_COLOR = 'white'

    BASE_FORMAT = {
        'font_family': 'Droid Serif',
        'font_color': 'black',
        'hoverlabel': {'font_color': 'white', 'bgcolor': 'black'}
    }

    AXIS_FORMAT = {
        'tickfont_size': TICK_SIZE,
        'title_font_size': LABEL_SIZE
    }

    TITLE_FORMAT = {
        'x': 0.5,
        'xanchor': 'center',
        'font_size': TITLE_SIZE,
        'y': 0.85
    }

    # Create the bar chart
    fig = px.bar(
        **FIG_SIZE,
        data_frame=aggregated_data,
        x='Day',
        y='Headcount',
        color='Month',
        color_discrete_sequence=px.colors.sequential.Plasma_r,
        category_orders={"Day": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
        title='Occupancy by Month and Weekday',
        barmode="group"
    )

    # Customize hover template
    fig.update_traces(hovertemplate='Headcount = %{y}')

    # Update layout
    fig.update_layout(
        **BASE_FORMAT,
        title=TITLE_FORMAT,
        xaxis={
            'title': {'text': 'Day of the week', 'font_size': LABEL_SIZE},
            'tickmode': 'array',
            'tickfont': {'size': TICK_SIZE},
            'categoryorder': 'array',
            'categoryarray': ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        },
        yaxis={
            'title': {'text': 'Headcount', 'font_size': LABEL_SIZE},
            'tickfont': {'size': TICK_SIZE},
            'gridcolor': 'rgba(128, 128, 128, 0.5)'
        },
        plot_bgcolor=PLOT_COLOR,
        paper_bgcolor=PAPER_COLOR,
        showlegend=True
    )

    # Show the figure
    fig.show()

    # Save the visualization
    filename_prefix = f"{semester_name}_" if semester_name else ""
    output_filename = f"{filename_prefix}occupancy_by_month.html"
    fig.write_html(output_filename)
    print(f"Visualization saved as {output_filename}")
