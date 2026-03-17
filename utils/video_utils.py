import cv2
import os
import subprocess


def get_video_info(video_path):
    """Extract metadata from a video file."""
    cap = cv2.VideoCapture(video_path)
    info = {
        'fps': cap.get(cv2.CAP_PROP_FPS) or 25.0,
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'total_frames': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }
    cap.release()
    return info


def read_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    return frames


def save_video(output_video_frames, output_video_path, fps=None):
    """Save video frames as H.264 MP4 with faststart via ffmpeg for browser compatibility."""
    if len(output_video_frames) == 0:
        print("Warning: No frames to save.")
        return

    if fps is None:
        fps = 25.0

    height, width = output_video_frames[0].shape[:2]

    # Write frames to a temporary AVI file using OpenCV XVID codec
    temp_dir = os.path.dirname(output_video_path) or '.'
    temp_path = os.path.join(temp_dir, '_temp_output.avi')
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(temp_path, fourcc, fps, (width, height))
    for frame in output_video_frames:
        out.write(frame)
    out.release()

    # Ensure output path ends with .mp4
    if not output_video_path.lower().endswith('.mp4'):
        output_video_path = os.path.splitext(output_video_path)[0] + '.mp4'

    # Re-encode to H.264 MP4 with faststart for browser playback
    cmd = [
        'ffmpeg', '-y',
        '-i', temp_path,
        '-c:v', 'libx264',
        '-preset', 'medium',
        '-crf', '23',
        '-movflags', '+faststart',
        '-pix_fmt', 'yuv420p',
        output_video_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Video saved: {output_video_path}")
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install ffmpeg (e.g., 'winget install ffmpeg' on Windows, 'brew install ffmpeg' on macOS).")
        print(f"Temporary AVI saved at: {temp_path}")
        return
    except subprocess.CalledProcessError as e:
        print(f"Error: ffmpeg encoding failed: {e.stderr}")
        print(f"Temporary AVI saved at: {temp_path}")
        return

    # Clean up temp file on success
    try:
        os.remove(temp_path)
    except OSError:
        pass
