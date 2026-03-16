from ultralytics import YOLO
import supervision as sv
import pickle
import os
import sys
import cv2
sys.path.append('../')
from utils import get_center_of_bbox, get_bbox_width
import numpy as np
import pandas as pd 

class Tracker:
    def __init__(self, model_path, conf=0.1):
        self.model = YOLO(model_path)
        self.tracker = sv.ByteTrack()
        self.conf = conf

    def interpolate_ball_positions(self, ball_positions):
        ball_positions = [x.get(1,{}).get('bbox', []) for x in ball_positions]
        df_ball_positions = pd.DataFrame(ball_positions, columns=['x1', 'y1', 'x2', 'y2'])

        #interpolate missing values
        df_ball_positions = df_ball_positions.interpolate()
        df_ball_positions = df_ball_positions.bfill()

        ball_positions = [{1: {"bbox": x}}for x in df_ball_positions.to_numpy().tolist()]

        return ball_positions

    def add_position_to_track(self, tracks):
        for object, object_tracks in tracks.items():
            for frame_num, frame_track in enumerate(object_tracks):
                for track_id, track_info in frame_track.items():
                    bbox = track_info['bbox']
                    position = get_center_of_bbox(bbox)
                    tracks[object][frame_num][track_id]['position'] = position

    def detect_frames(self, frames):
        batch_size=20
        detections = []
        for i in range(0, len(frames), batch_size):
            detections_batch = self.model.predict(frames[i:i+batch_size], conf=self.conf)
            detections += detections_batch

        return detections

    def get_object_tracks(self, frames, read_from_stub=False, stub_path=None):
        
        if read_from_stub and stub_path is not None and os.path.exists(stub_path):
            with open(stub_path, 'rb') as f:
                tracks = pickle.load(f)
            return tracks

        detections = self.detect_frames(frames)

        tracks ={
            "players": [],
            "referees": [],
            "ball": []
        }

        for frame_num, detection in enumerate(detections): 
            cls_names = detection.names
            cls_names_inv = {v:k for k, v in cls_names.items()}

            #Convert to supervision detection format
            detection_supervision = sv.Detections.from_ultralytics(detection)

            #Convert goalkeeper to player object
            for object_ind, class_id in enumerate(detection_supervision.class_id):
                if cls_names[class_id] == "goalkeeper":
                    detection_supervision.class_id[object_ind] = cls_names_inv["player"]

            #track objects
            detections_with_tracks = self.tracker.update_with_detections(detection_supervision)

            tracks["players"].append({})
            tracks["referees"].append({})
            tracks["ball"].append({})

            for frame_detection in detections_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]
                track_id = frame_detection[4]

                if cls_id == cls_names_inv.get('player'):
                    tracks["players"][frame_num][track_id] = {"bbox": bbox}

                if cls_id == cls_names_inv.get('referee'):
                    tracks["referees"][frame_num][track_id] = {"bbox": bbox}

            for frame_detection in detections_with_tracks:
                bbox = frame_detection[0].tolist()
                cls_id = frame_detection[3]

                if cls_id == cls_names_inv.get('ball'):
                    tracks["ball"][frame_num][1] = {"bbox": bbox}

        if stub_path is not None:
            with open(stub_path, 'wb') as f:
                pickle.dump(tracks, f)

        return tracks

    def draw_ellipse(self, frame, bbox, color, track_id):
        y2 = int(bbox[3])

        x_center, _ = get_center_of_bbox(bbox)
        width = get_bbox_width(bbox)

        cv2.ellipse(
            frame,
            (x_center, y2),
            axes=(int(width), int(.35*width)),
            angle=0,
            startAngle=-45,
            endAngle=235,
            color=color,
            thickness=2,
            lineType=cv2.LINE_4,
        )

        rectangle_width = 40
        rectangle_height = 20
        x1_rect = x_center - rectangle_width // 2
        x2_rect = x_center + rectangle_width // 2
        y1_rect= (y2-rectangle_height//2) +15
        y2_rect = (y2+rectangle_height//2) +15

        if track_id is not None:
            cv2.rectangle(frame, (int(x1_rect), int(y1_rect)), (int(x2_rect), int(y2_rect)), color, cv2.FILLED)
            
            x1_text = x1_rect+12
            if track_id >= 99:
                x1_text -=10

            cv2.putText(frame, f"{track_id}", (int(x1_text), int(y1_rect + 15)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        return frame

    def draw_triangle(self, frame, bbox, color):
        y = int(bbox[1])
        x,_ = get_center_of_bbox(bbox)

        triangle_points = np.array([[x, y], [x-10, y-20], [x+10, y-20]])

        cv2.drawContours(frame, [triangle_points], 0, color, cv2.FILLED)
        cv2.drawContours(frame, [triangle_points], 0, (0, 0, 0), 2)
        return frame
    
    
    def draw_team_ball_control(self, frame, team_ball_control, frame_num):
        """Draw possession overlay — position scales to any resolution."""
        h, w = frame.shape[:2]

        # Position the overlay relative to frame size (bottom-right area)
        overlay_w, overlay_h = int(w * 0.3), int(h * 0.13)
        x1 = w - overlay_w - int(w * 0.02)
        y1 = h - overlay_h - int(h * 0.02)
        x2 = x1 + overlay_w
        y2 = y1 + overlay_h

        overlay = frame.copy()
        cv2.rectangle(overlay, (x1, y1), (x2, y2), (255,255,255), cv2.FILLED)
        alpha = 0.4
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

        team_ball_control_till_frame = team_ball_control[:frame_num+1]
        team_1_num_frames = team_ball_control_till_frame[team_ball_control_till_frame == 1].shape[0]
        team_2_num_frames = team_ball_control_till_frame[team_ball_control_till_frame == 2].shape[0]

        total = team_1_num_frames + team_2_num_frames
        team_1 = team_1_num_frames / max(total, 1)
        team_2 = team_2_num_frames / max(total, 1)

        font_scale = max(0.4, min(h / 1800, 0.8))
        thickness = max(1, int(h / 500))
        text_x = x1 + int(overlay_w * 0.05)
        cv2.putText(frame, f"Team 1 Ball Control: {team_1*100:.1f}%", (text_x, y1 + int(overlay_h * 0.4)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
        cv2.putText(frame, f"Team 2 Ball Control: {team_2*100:.1f}%", (text_x, y1 + int(overlay_h * 0.8)), cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness)
        return frame


    def draw_annotations(self, frames, tracks, team_ball_control):
        output_video_frames = []
        for frame_num, frame in enumerate(frames):
            frame = frame.copy()

            player_dict = tracks["players"][frame_num]
            referee_dict = tracks["referees"][frame_num]
            ball_dict = tracks["ball"][frame_num]

            # Draw players
            for track_id, player in player_dict.items():
                color = player.get("team_color", (0, 0, 255))
                frame = self.draw_ellipse(frame, player["bbox"], color, track_id)

                if player.get("has_ball", False):
                    frame = self.draw_triangle(frame, player["bbox"], (0, 0, 255))

            # Draw referees
            for _, referee in referee_dict.items():
                frame = self.draw_ellipse(frame, referee["bbox"], (255, 0, 0), None)

            # Draw ball
            for track_id, ball in ball_dict.items():
                frame = self.draw_triangle(frame, ball["bbox"], (0, 255, 255))

            frame = self.draw_team_ball_control(frame, team_ball_control, frame_num)

            output_video_frames.append(frame)

        return output_video_frames

    