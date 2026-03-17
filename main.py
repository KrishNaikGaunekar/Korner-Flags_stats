import argparse
import os
import json
import cv2
import numpy as np

from team_assigner import TeamAssigner
from utils import read_video, save_video, get_video_info
from trackers import Tracker
from player_ball_assigner import PlayerBallAssigner
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distnace_estimator import SpeedAndDistanceEstimator


def parse_args():
    parser = argparse.ArgumentParser(description='Korner Flags - Soccer Video Analysis')
    parser.add_argument('--input', '-i', type=str, required=True,
                        help='Path to input video file (mp4, mov, avi, webm)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Path to output video file (default: output_videos/<input_name>_annotated.mp4)')
    parser.add_argument('--model', '-m', type=str, default='models/best.pt',
                        help='Path to YOLO model weights (default: models/best.pt)')
    parser.add_argument('--use-stubs', action='store_true',
                        help='Use cached stub files if available (for development only)')
    parser.add_argument('--confidence', type=float, default=0.1,
                        help='YOLO detection confidence threshold (default: 0.1)')
    parser.add_argument('--stats-output', type=str, default=None,
                        help='Path to save stats JSON (default: alongside output video)')
    return parser.parse_args()


def main():
    args = parse_args()

    # Validate input
    if not os.path.exists(args.input):
        print(f"Error: Input video not found: {args.input}")
        return

    # Set up output path
    if args.output is None:
        os.makedirs('output_videos', exist_ok=True)
        input_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = f'output_videos/{input_name}_annotated.mp4'

    # Get video metadata (fps, resolution) from the input
    video_info = get_video_info(args.input)
    print(f"Input video: {args.input}")
    print(f"  Resolution: {video_info['width']}x{video_info['height']}")
    print(f"  FPS: {video_info['fps']}")
    print(f"  Frames: {video_info['total_frames']}")

    # Read Video
    print("Reading video frames...")
    video_frames = read_video(args.input)

    if len(video_frames) == 0:
        print("Error: Could not read any frames from the video.")
        return

    # Initialize Tracker
    print(f"Loading YOLO model: {args.model}")
    tracker = Tracker(args.model, conf=args.confidence)

    # Detect and track objects
    stub_path = 'stubs/tracks_stubs.pkl' if args.use_stubs else None
    tracks = tracker.get_object_tracks(
        video_frames,
        read_from_stub=args.use_stubs,
        stub_path=stub_path
    )

    # Get object positions
    tracker.add_position_to_track(tracks)

    # Camera movement estimation
    print("Estimating camera movement...")
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    cam_stub = 'stubs/camera_movement_stubs.pkl' if args.use_stubs else None
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(
        video_frames,
        read_from_stub=args.use_stubs,
        stub_path=cam_stub
    )
    camera_movement_estimator.add_adjust_position_to_tracks(tracks, camera_movement_per_frame)

    # View transformation (auto-detect from frame dimensions)
    print("Applying perspective transformation...")
    view_transformer = ViewTransformer(
        frame_width=video_info['width'],
        frame_height=video_info['height']
    )
    view_transformer.add_transformered_position_to_tracks(tracks)

    # Interpolate ball positions to fill gaps
    tracks['ball'] = tracker.interpolate_ball_positions(tracks['ball'])

    # Speed and distance estimation (using actual fps from video)
    print("Calculating speed and distance...")
    speed_and_distance_estimator = SpeedAndDistanceEstimator(frame_rate=video_info['fps'])
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)

    # Assign player teams
    print("Classifying teams...")
    team_assigner = TeamAssigner()
    team_assigner.assign_teams(video_frames[0], tracks['players'][0])
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]

    # Ball possession tracking with smoothing
    print("Tracking ball possession...")
    player_assigner = PlayerBallAssigner()
    team_ball_control = [1]
    raw_detections = [1]
    consecutive_frames_threshold = 15

    for frame_num, player_track in enumerate(tracks['players']):
        ball_box = tracks['ball'][frame_num].get(1, {}).get('bbox', None)
        if ball_box is None:
            raw_detections.append(raw_detections[-1])
            team_ball_control.append(team_ball_control[-1])
            continue

        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_box)

        if assigned_player != -1:
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            new_team = tracks['players'][frame_num][assigned_player]['team']
            raw_detections.append(new_team)

            consecutive_count = 0
            for i in range(len(raw_detections) - 1, max(0, len(raw_detections) - consecutive_frames_threshold - 1), -1):
                if raw_detections[i] == new_team:
                    consecutive_count += 1
                else:
                    break

            if new_team == team_ball_control[-1] or consecutive_count >= consecutive_frames_threshold:
                team_ball_control.append(new_team)
            else:
                team_ball_control.append(team_ball_control[-1])
        else:
            raw_detections.append(raw_detections[-1])
            team_ball_control.append(team_ball_control[-1])

    team_ball_control = np.array(team_ball_control)

    # Draw output annotations
    print("Drawing annotations...")
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames, camera_movement_per_frame)
    output_video_frames = speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

    # Save video (using input video's actual fps)
    print(f"Saving output to: {args.output}")
    save_video(output_video_frames, args.output, fps=video_info['fps'])

    # Generate and save stats JSON
    stats = generate_stats(tracks, team_ball_control, video_info)
    stats_path = args.stats_output or os.path.splitext(args.output)[0] + '_stats.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Stats saved to: {stats_path}")

    # Export positions JSON for heatmap generation
    positions_path = os.path.splitext(args.output)[0].replace('_annotated', '') + '_positions.json'
    export_positions(tracks, video_info, positions_path)
    print(f"Positions saved to: {positions_path}")

    print("Done!")


def generate_stats(tracks, team_ball_control, video_info):
    """Generate summary statistics from the processed tracks (DATA-03)."""
    total_frames = len(tracks['players'])

    # Possession stats
    team_1_frames = int(np.sum(team_ball_control == 1))
    team_2_frames = int(np.sum(team_ball_control == 2))
    total_possession = team_1_frames + team_2_frames

    # Collect per-player speed lists, distances, and teams across all frames
    player_speeds = {}    # {pid: [speed1, speed2, ...]}
    player_team = {}      # {pid: team_int}
    player_distance = {}  # {pid: latest_distance}
    for frame_tracks in tracks['players']:
        for pid, info in frame_tracks.items():
            if 'speed' in info and info['speed'] is not None:
                player_speeds.setdefault(pid, []).append(info['speed'])
            if 'distance' in info and info['distance'] is not None:
                player_distance[pid] = info['distance']
            if 'team' in info and info['team'] is not None:
                player_team[pid] = info['team']

    # Build per-player nested dict
    players = {}
    for pid in player_team:
        speeds = player_speeds.get(pid, [])
        players[str(pid)] = {
            'team': int(player_team[pid]),
            'distance_m': round(float(player_distance.get(pid, 0)), 1),
            'max_speed_kmh': round(float(max(speeds)) if speeds else 0.0, 1),
            'avg_speed_kmh': round(float(sum(speeds) / len(speeds)) if speeds else 0.0, 1),
        }

    return {
        'video': {
            'fps': video_info['fps'],
            'resolution': f"{video_info['width']}x{video_info['height']}",
            'total_frames': total_frames,
            'duration_seconds': round(total_frames / video_info['fps'], 1),
        },
        'possession': {
            'team_1_percent': round(team_1_frames / max(total_possession, 1) * 100, 1),
            'team_2_percent': round(team_2_frames / max(total_possession, 1) * 100, 1),
        },
        'players': players,
    }


def export_positions(tracks, video_info, output_path):
    """Export per-player positions at 1 Hz for heatmap generation (DATA-01)."""
    fps = video_info['fps']
    sample_interval = round(fps)  # 1 Hz downsampling
    records = []
    for frame_num, player_track in enumerate(tracks['players']):
        if frame_num % sample_interval != 0:
            continue
        second = int(frame_num / fps)
        for player_id, info in player_track.items():
            pos = info.get('position_transformed')
            team = info.get('team')
            if pos is None or team is None:
                continue
            records.append({
                'second': second,
                'player_id': int(player_id),
                'x': round(float(pos[0]), 2),
                'y': round(float(pos[1]), 2),
                'team': int(team),
            })
    data = {
        'fps': fps,
        'sample_rate_hz': 1,
        'positions': records,
    }
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)


if __name__ == '__main__':
    main()
