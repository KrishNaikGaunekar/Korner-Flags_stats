import numpy as np
import cv2

class ViewTransformer():
    def __init__(self, frame_width=1920, frame_height=1080, pixel_vertices=None):
        """
        Initialize perspective transformer.
        
        Args:
            frame_width: Width of the video frame in pixels
            frame_height: Height of the video frame in pixels  
            pixel_vertices: Optional manual 4-point array [[x,y], ...] for the pitch corners.
                           If None, estimates proportionally from frame dimensions.
        """
        court_width = 68     # standard soccer pitch width in meters
        court_length = 23.32 # visible portion of pitch length in meters

        if pixel_vertices is not None:
            self.pixel_verticies = np.array(pixel_vertices, dtype=np.float32)
        else:
            # Estimate pitch corner positions proportionally from frame size.
            # These ratios are derived from the original 1920x1080 calibration:
            #   [110, 1035] -> [0.057, 0.958]
            #   [265, 275]  -> [0.138, 0.255]
            #   [910, 260]  -> [0.474, 0.241]
            #   [1640, 915] -> [0.854, 0.847]
            # This works for standard broadcast camera angles. For significantly
            # different angles, pass pixel_vertices manually.
            self.pixel_verticies = np.array([
                [int(0.057 * frame_width), int(0.958 * frame_height)],  # bottom-left
                [int(0.138 * frame_width), int(0.255 * frame_height)],  # top-left
                [int(0.474 * frame_width), int(0.241 * frame_height)],  # top-right
                [int(0.854 * frame_width), int(0.847 * frame_height)],  # bottom-right
            ], dtype=np.float32)

        self.target_verticies = np.array(
            [[0, court_width], [0, 0], [court_length, 0], [court_length, court_width]],
            dtype=np.float32
        )

        self.perspective_transformer = cv2.getPerspectiveTransform(
            self.pixel_verticies, self.target_verticies
        )
    
    def transform_point(self, point):
        reshaped_point = point.reshape(-1,1,2).astype(np.float32)
        transformed_point = cv2.perspectiveTransform(reshaped_point, self.perspective_transformer)
        return transformed_point.reshape(-1,2)

    def add_transformered_position_to_tracks(self, tracks):
        for object, object_tracks in tracks.items():
            for frame_num, track in enumerate(object_tracks):
                for track_id, track_info in track.items():
                    position = track_info.get('position_adjusted')
                    if position is None:
                        tracks[object][frame_num][track_id]['position_transformed'] = None
                        continue
                    position = np.array(position)
                    position_transformed = self.transform_point(position)
                    if position_transformed is not None:
                        position_transformed = position_transformed.squeeze().tolist()
                    tracks[object][frame_num][track_id]['position_transformed'] = position_transformed