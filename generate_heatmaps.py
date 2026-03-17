"""Generate team heatmap PNGs from positions.json (DATA-02).

Usage:
    python generate_heatmaps.py --positions output_videos/08fd33_4_positions.json

Outputs:
    output_videos/08fd33_4_heatmap_team1.png
    output_videos/08fd33_4_heatmap_team2.png
"""
import argparse
import json
import os
import sys

import matplotlib
matplotlib.use('Agg')  # headless backend — MUST be before pyplot import
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter


def load_positions(path):
    """Load positions.json and split coordinates by team."""
    with open(path) as f:
        data = json.load(f)
    team1_x, team1_y = [], []
    team2_x, team2_y = [], []
    for record in data['positions']:
        if record['team'] == 1:
            team1_x.append(record['x'])
            team1_y.append(record['y'])
        elif record['team'] == 2:
            team2_x.append(record['x'])
            team2_y.append(record['y'])
    return (
        np.array(team1_x), np.array(team1_y),
        np.array(team2_x), np.array(team2_y),
    )


def generate_heatmap(x_coords, y_coords, team_label, cmap_name, output_path):
    """Generate a single team heatmap PNG on a green pitch background.

    Args:
        x_coords: numpy array of x positions (meters, 0-23.32 range)
        y_coords: numpy array of y positions (meters, 0-68 range)
        team_label: title string, e.g. "Team 1"
        cmap_name: matplotlib colormap name, e.g. "Blues" or "Reds"
        output_path: path to save the PNG
    """
    pitch = Pitch(
        pitch_type='custom',
        pitch_length=23.32,
        pitch_width=68,
        pitch_color='grass',
        line_color='white',
        line_zorder=2,
    )
    fig, ax = pitch.draw(figsize=(12, 8))  # 12x8 inches @ 100 dpi = 1200x800 px
    fig.patch.set_facecolor('#2e8b2e')  # dark green background matching grass

    if len(x_coords) > 0:
        bin_statistic = pitch.bin_statistic(
            x_coords, y_coords, statistic='count', bins=(25, 25)
        )
        bin_statistic['statistic'] = gaussian_filter(bin_statistic['statistic'], 1)
        pitch.heatmap(bin_statistic, ax=ax, cmap=cmap_name, edgecolors='none', alpha=0.7)

    ax.set_title(team_label, fontsize=16, color='white', pad=10)
    # Save without bbox_inches='tight' to preserve the 1200x800 target dimensions
    fig.savefig(output_path, dpi=100, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description='Generate team heatmap PNGs from positions.json')
    parser.add_argument('--positions', '-p', required=True,
                        help='Path to positions.json file')
    args = parser.parse_args()

    if not os.path.exists(args.positions):
        print(f'Error: positions file not found: {args.positions}')
        sys.exit(1)

    stem = os.path.splitext(args.positions)[0]  # e.g. output_videos/08fd33_4_positions
    stem = stem.replace('_positions', '')         # e.g. output_videos/08fd33_4

    team1_x, team1_y, team2_x, team2_y = load_positions(args.positions)

    out1 = f'{stem}_heatmap_team1.png'
    out2 = f'{stem}_heatmap_team2.png'

    print(f'Generating Team 1 heatmap ({len(team1_x)} positions)...')
    generate_heatmap(team1_x, team1_y, 'Team 1', 'Blues', out1)
    print(f'  Saved: {out1}')

    print(f'Generating Team 2 heatmap ({len(team2_x)} positions)...')
    generate_heatmap(team2_x, team2_y, 'Team 2', 'Reds', out2)
    print(f'  Saved: {out2}')


if __name__ == '__main__':
    main()
