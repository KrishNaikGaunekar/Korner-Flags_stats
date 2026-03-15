import cv2
from matplotlib.pyplot import box
from team_assigner import TeamAssigner
from utils import read_video, save_video
from trackers import Tracker
from player_ball_assigner import PlayerBallAssigner
import numpy as np
from camera_movement_estimator import CameraMovementEstimator
from view_transformer import ViewTransformer
from speed_and_distnace_estimator import SpeedAndDistanceEstimator
def main():
    # Read Video
    video_frames = read_video(r"C:\Korner flag\Input video\08fd33_4.mp4")


    

    #Initialize Tracker
    tracker = Tracker('models/best.pt')

    tracks = tracker.get_object_tracks(video_frames, read_from_stub=True, stub_path='stubs/tracks_stubs.pkl')

    #get object positions
    tracker.add_position_to_track(tracks)
    

    #camera movement estimation
    camera_movement_estimator = CameraMovementEstimator(video_frames[0])
    camera_movement_per_frame = camera_movement_estimator.get_camera_movement(video_frames, read_from_stub=True, stub_path='stubs/camera_movement_stubs.pkl')
    camera_movement_estimator.add_adjust_position_to_tracks(tracks, camera_movement_per_frame)

    #vew transformation
    view_transformer = ViewTransformer()
    view_transformer.add_transformered_position_to_tracks(tracks)


    tracks['ball'] = tracker.interpolate_ball_positions(tracks['ball'])

    #speed and distance estimation
    speed_and_distance_estimator = SpeedAndDistanceEstimator()
    speed_and_distance_estimator.add_speed_and_distance_to_tracks(tracks)


    #assign players teams
    team_assigner = TeamAssigner()
    team_assigner.assign_teams(video_frames[0], tracks['players'][0])
    for frame_num, player_track in enumerate(tracks['players']):
        for player_id, track in player_track.items():
            team = team_assigner.get_player_team(video_frames[frame_num], track['bbox'], player_id)
            tracks['players'][frame_num][player_id]['team'] = team
            tracks['players'][frame_num][player_id]['team_color'] = team_assigner.team_colors[team]

    player_assigner = PlayerBallAssigner()
    team_ball_control = [1]  # Start with Team 1 possession
    raw_detections = [1]  # Track raw ball detections separately
    consecutive_frames_threshold = 15  # Require 15 frames before switching possession

    for frame_num, player_track in enumerate(tracks['players']):
        ball_box = tracks['ball'][frame_num][1]['bbox']
        assigned_player = player_assigner.assign_ball_to_player(player_track, ball_box)

        if assigned_player != -1:
            tracks['players'][frame_num][assigned_player]['has_ball'] = True
            new_team = tracks['players'][frame_num][assigned_player]['team']
            raw_detections.append(new_team)

            # Count consecutive frames for this team in raw detections
            consecutive_count = 0
            for i in range(len(raw_detections) - 1, max(0, len(raw_detections) - consecutive_frames_threshold - 1), -1):
                if raw_detections[i] == new_team:
                    consecutive_count += 1
                else:
                    break

            # Only switch if team has had ball for enough frames, or same team
            if new_team == team_ball_control[-1] or consecutive_count >= consecutive_frames_threshold:
                team_ball_control.append(new_team)
            else:
                team_ball_control.append(team_ball_control[-1])
        else:
            raw_detections.append(raw_detections[-1])
            team_ball_control.append(team_ball_control[-1])

    team_ball_control = np.array(team_ball_control)


    # Draw output
    ## Draw object Tracks
    output_video_frames = tracker.draw_annotations(video_frames, tracks, team_ball_control)

    ## Draw camera movement
    output_video_frames = camera_movement_estimator.draw_camera_movement(output_video_frames, camera_movement_per_frame)


    ##draw speed and distance
    output_video_frames = speed_and_distance_estimator.draw_speed_and_distance(output_video_frames, tracks)

    
    # Save video
    save_video(output_video_frames, 'output_videos/output_video.avi')


if __name__ == '__main__':
    main()

