import sys
import numpy as np
import pandas as pd

from nba_api.stats.static import players
from nba_api.stats.endpoints import shotchartdetail, playercareerstats

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Arc


def get_player_shotchartdetail(player_name, season_id):
    """
    Fetches the shot chart details for a given player and season.
    
    Parameters:
        player_name (str): Full name of the player.
        season_id (str): NBA season ID (e.g., "2024-25").
    
    Returns:
        tuple: DataFrames containing the player's shot data and league averages.
    """
    # Get player info
    nba_players = players.get_players()
    player = next((p for p in nba_players if p['full_name'] == player_name), None)
    if not player:
        raise ValueError(f"Player '{player_name}' not found.")

    # Fetch career stats and team ID for the season
    career = playercareerstats.PlayerCareerStats(player_id=player['id'])
    career_df = career.get_data_frames()[0]
    team_id = career_df.loc[career_df['SEASON_ID'] == season_id, 'TEAM_ID'].iloc[0]

    # Fetch shot chart data
    shotchart = shotchartdetail.ShotChartDetail(
        team_id=int(team_id),
        player_id=int(player['id']),
        season_type_all_star='Regular Season',
        season_nullable=season_id,
        context_measure_simple="FGA"
    ).get_data_frames()

    return shotchart[0], shotchart[1]


def draw_court(ax=None, color="blue", lw=1, outer_lines=False):
    """
    Draws a basketball court on the given axis.
    """
    if ax is None:
        ax = plt.gca()

    # Define court elements
    court_elements = [
        Circle((0, 0), radius=7.5, linewidth=lw, color=color, fill=False),  # Hoop
        Rectangle((-30, -12.5), 60, 0, linewidth=lw, color=color),         # Backboard
        Rectangle((-80, -47.5), 160, 190, linewidth=lw, color=color, fill=False),  # Paint (outer box)
        Rectangle((-60, -47.5), 120, 190, linewidth=lw, color=color, fill=False),  # Paint (inner box)
        Arc((0, 142.5), 120, 120, theta1=0, theta2=180, linewidth=lw, color=color),  # Free-throw top
        Arc((0, 142.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color), # Free-throw bottom
        Arc((0, 0), 80, 80, theta1=0, theta2=180, linewidth=lw, color=color),       # Restricted area
        Rectangle((-220, -47.5), 0, 140, linewidth=lw, color=color),               # Corner 3A
        Rectangle((220, -47.5), 0, 140, linewidth=lw, color=color),                # Corner 3B
        Arc((0, 0), 475, 475, theta1=22, theta2=158, linewidth=lw, color=color),   # 3-point arc
        Arc((0, 422.5), 120, 120, theta1=180, theta2=0, linewidth=lw, color=color), # Center court outer
        Arc((0, 422.5), 40, 40, theta1=180, theta2=0, linewidth=lw, color=color)   # Center court inner
    ]

    if outer_lines:
        court_elements.append(Rectangle((-250, -47.5), 500, 470, linewidth=lw, color=color, fill=False))

    for element in court_elements:
        ax.add_patch(element)


def plot_shot_chart(data, title="", ax=None, court_color="white", court_lw=2, line_color="blue"):
    """
    Plots the shot chart.
    """
    if ax is None:
        ax = plt.gca()

    # Configure axis
    ax.set_xlim(-250, 250)
    ax.set_ylim(422.5, -47.5)
    ax.set_title(title, fontsize=18)
    ax.tick_params(labelbottom=False, labelleft=False)

    # Draw court
    draw_court(ax, color=line_color, lw=court_lw)

    # Plot shots
    ax.scatter(data.loc[data['EVENT_TYPE'] == 'Missed Shot', 'LOC_X'],
               data.loc[data['EVENT_TYPE'] == 'Missed Shot', 'LOC_Y'],
               c='r', marker="x", s=100, linewidths=1, label="Missed")
    ax.scatter(data.loc[data['EVENT_TYPE'] == 'Made Shot', 'LOC_X'],
               data.loc[data['EVENT_TYPE'] == 'Made Shot', 'LOC_Y'],
               edgecolors='g', facecolors='none', marker='o', s=100, linewidths=1, label="Made")
    ax.legend()


if __name__ == "__main__":
    # Handle CLI arguments
    player_name = sys.argv[1] if len(sys.argv) > 1 else "Zach Edey"
    season_id = sys.argv[2] if len(sys.argv) > 2 else "2024-25"

    # Get data and plot shot chart
    shot_data, _ = get_player_shotchartdetail(player_name, season_id)
    plt.figure(figsize=(12, 11))
    plot_shot_chart(shot_data, title=f"{player_name} Shot Chart {season_id}")
    plt.show()
