import cv2

import os

def read_video(video_path):
    print(f"🎬 Loading video from: {video_path}")
    video_path = os.path.abspath(video_path)
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"❌ File does not exist: {video_path}")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise IOError(f"🚫 OpenCV failed to open the video: {video_path}")

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)
    cap.release()
    print(f"✅ Loaded {len(frames)} frames from: {video_path}")
    return frames

# def read_video(video_path):
#     cap = cv2.VideoCapture(video_path)
#     frames = []
#     while True:
#         ret, frame = cap.read()
#         if not ret:
#             break
#         frames.append(frame)
#     cap.release()
#     return frames

def save_video(frames, output_path):
    if not frames:
        print("No frames to save!")
        return
    
    # Ensure output folder exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    height, width, _ = frames[0].shape
    
    # Use MP4 codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # 'mp4v' works well for .mp4 files
    
    out = cv2.VideoWriter(output_path, fourcc, 24, (width, height))
    
    for frame in frames:
        out.write(frame)
    out.release()
    print(f"Video saved to: {output_path}")
