# from utils import (
#     read_video,
#     save_video,
#     measure_distance,
#     draw_player_stats,
#     convert_pixel_distance_to_meters
# )
# import constants
# from trackers import PlayerTracker, BallTracker
# from court_line_detector import CourtLineDetector
# from mini_court import MiniCourt

# import pandas as pd
# from copy import deepcopy
# import cv2
# import os

# def run_analysis(input_video_path, output_video_path):
#     input_video_path = os.path.abspath(input_video_path)
#     output_video_path = os.path.abspath(output_video_path)
#     # Add FPS detection here
#     cap = cv2.VideoCapture(input_video_path)
#     fps = cap.get(cv2.CAP_PROP_FPS)
#     if fps <= 0:
#         fps = 24
#     cap.release()
    

    
    
#     video_frames = read_video(input_video_path)
#     if not video_frames:
#         raise ValueError(f"No frames found in video: {input_video_path}")

#     # Your existing main() logic here, just indent it all one level,
#     # replace hardcoded paths with parameters.

#     # Detect Players and Ball
#     player_tracker = PlayerTracker(model_path='yolov8x')
#     ball_tracker = BallTracker(model_path='models/yolo5_last.pt')

#     player_detections = player_tracker.detect_frames(
#         video_frames,
#         read_from_stub=True,
#         stub_path="tracker_stubs/player_detections.pkl"
#     )
#     ball_detections = ball_tracker.detect_frames(
#         video_frames,
#         read_from_stub=True,
#         stub_path="tracker_stubs/ball_detections.pkl"
#     )
#     ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)

#     # Court Line Detection
#     court_model_path = "models/keypoints_model.pth"
#     court_line_detector = CourtLineDetector(court_model_path)
#     court_keypoints = court_line_detector.predict(video_frames[0])

#     # Choose players
#     player_detections = player_tracker.choose_and_filter_players(
#         court_keypoints, player_detections)

#     # Mini Court setup
#     mini_court = MiniCourt(video_frames[0])
#     ball_shot_frames = ball_tracker.get_ball_shot_frames(ball_detections)

#     # Convert to mini court coordinates
#     player_mini_detections, ball_mini_detections = mini_court.convert_bounding_boxes_to_mini_court_coordinates(
#         player_detections, ball_detections, court_keypoints)

#     player_stats_data = [{
#         'frame_num': 0,
#         'player_1_number_of_shots': 0,
#         'player_1_total_shot_speed': 0,
#         'player_1_last_shot_speed': 0,
#         'player_1_total_player_speed': 0,
#         'player_1_last_player_speed': 0,

#         'player_2_number_of_shots': 0,
#         'player_2_total_shot_speed': 0,
#         'player_2_last_shot_speed': 0,
#         'player_2_total_player_speed': 0,
#         'player_2_last_player_speed': 0,
#     }]
#     for ball_shot_ind in range(len(ball_shot_frames) - 1):
#         start_frame = ball_shot_frames[ball_shot_ind]
#         end_frame = ball_shot_frames[ball_shot_ind + 1]
#         # Use actual fps here
#         ball_shot_time = (end_frame - start_frame) / fps
        
  
#         start_frame = ball_shot_frames[ball_shot_ind]
#         end_frame = ball_shot_frames[ball_shot_ind + 1]
#         ball_shot_time = (end_frame - start_frame) / 24  # fps = 24

#         ball_distance_px = measure_distance(
#             ball_mini_detections[start_frame][1],
#             ball_mini_detections[end_frame][1]
#         )
#         ball_distance_m = convert_pixel_distance_to_meters(
#             ball_distance_px,
#             constants.DOUBLE_LINE_WIDTH,
#             mini_court.get_width_of_mini_court()
#         )
#         ball_speed = (ball_distance_m / ball_shot_time) * 3.6  # km/h

#         player_positions = player_mini_detections[start_frame]
#         player_shot_ball = min(player_positions.keys(), key=lambda pid: measure_distance(
#             player_positions[pid], ball_mini_detections[start_frame][1]))

#         opponent_id = 1 if player_shot_ball == 2 else 2
#         opp_distance_px = measure_distance(
#             player_mini_detections[start_frame][opponent_id],
#             player_mini_detections[end_frame][opponent_id]
#         )
#         opp_distance_m = convert_pixel_distance_to_meters(
#             opp_distance_px,
#             constants.DOUBLE_LINE_WIDTH,
#             mini_court.get_width_of_mini_court()
#         )
#         opp_speed = (opp_distance_m / ball_shot_time) * 3.6

#         stats = deepcopy(player_stats_data[-1])
#         stats['frame_num'] = start_frame
#         stats[f'player_{player_shot_ball}_number_of_shots'] += 1
#         stats[f'player_{player_shot_ball}_total_shot_speed'] += ball_speed
#         stats[f'player_{player_shot_ball}_last_shot_speed'] = ball_speed

#         stats[f'player_{opponent_id}_total_player_speed'] += opp_speed
#         stats[f'player_{opponent_id}_last_player_speed'] = opp_speed

#         player_stats_data.append(stats)

#     df_stats = pd.DataFrame(player_stats_data)
#     frames_df = pd.DataFrame({'frame_num': list(range(len(video_frames)))})
#     df_stats = pd.merge(frames_df, df_stats, on='frame_num', how='left').ffill()

#     df_stats['player_1_average_shot_speed'] = df_stats['player_1_total_shot_speed'] / \
#         df_stats['player_1_number_of_shots']
#     df_stats['player_2_average_shot_speed'] = df_stats['player_2_total_shot_speed'] / \
#         df_stats['player_2_number_of_shots']
#     df_stats['player_1_average_player_speed'] = df_stats['player_1_total_player_speed'] / \
#         df_stats['player_2_number_of_shots']
#     df_stats['player_2_average_player_speed'] = df_stats['player_2_total_player_speed'] / \
#         df_stats['player_1_number_of_shots']

#     # Visual Output
#     output_frames = player_tracker.draw_bboxes(video_frames, player_detections)
#     output_frames = ball_tracker.draw_bboxes(output_frames, ball_detections)
#     output_frames = court_line_detector.draw_keypoints_on_video(
#         output_frames, court_keypoints)
#     output_frames = mini_court.draw_mini_court(output_frames)
#     output_frames = mini_court.draw_points_on_mini_court(
#         output_frames, player_mini_detections)
#     output_frames = mini_court.draw_points_on_mini_court(
#         output_frames, ball_mini_detections, color=(0, 255, 255))
#     output_frames = draw_player_stats(output_frames, df_stats)
#     print(f"Total frames to save: {len(output_frames)}")
        
#     # --- Insert your debug prints here ---
#     print(f"Total frames: {len(output_frames)}")
#     if len(output_frames) > 0:
#         print(f"Frame size: {output_frames[0].shape}, dtype: {output_frames[0].dtype}")
#     else:
#         print("No frames found to save!")
    
#     # Ensure output directory exists
#     os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
#     # Pass fps when saving video
#     save_video(output_frames, output_video_path, fps=fps)
#     return output_video_path


# if __name__ == "__main__":
    

#     default_input = "input_videos/input_video.mp4"
#     default_output = "output_videos/output_video.mp4"
#     run_analysis(default_input, default_output)
    
from utils import (
    read_video,
    save_video,
    measure_distance,
    draw_player_stats,
    convert_pixel_distance_to_meters
)
import constants
from trackers import PlayerTracker, BallTracker
from court_line_detector import CourtLineDetector
from mini_court import MiniCourt

import pandas as pd
from copy import deepcopy
import cv2
import os

def run_analysis(input_video_path, output_video_path):
    input_video_path = os.path.abspath(input_video_path)
    output_video_path = os.path.abspath(output_video_path)
    
    # Add FPS detection here
    cap = cv2.VideoCapture(input_video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 24
    cap.release()
    
    print(f"🎬 Detected FPS: {fps}")
    
    video_frames = read_video(input_video_path)
    if not video_frames:
        raise ValueError(f"No frames found in video: {input_video_path}")

    # Detect Players and Ball
    player_tracker = PlayerTracker(model_path='yolov8x')
    ball_tracker = BallTracker(model_path='models/yolo5_last.pt')

    player_detections = player_tracker.detect_frames(
        video_frames,
        read_from_stub=True,
        stub_path="tracker_stubs/player_detections.pkl"
    )
    ball_detections = ball_tracker.detect_frames(
        video_frames,
        read_from_stub=True,
        stub_path="tracker_stubs/ball_detections.pkl"
    )
    ball_detections = ball_tracker.interpolate_ball_positions(ball_detections)

    # Court Line Detection
    court_model_path = "models/keypoints_model.pth"
    court_line_detector = CourtLineDetector(court_model_path)
    court_keypoints = court_line_detector.predict(video_frames[0])

    # Choose players
    player_detections = player_tracker.choose_and_filter_players(
        court_keypoints, player_detections)

    # Mini Court setup
    mini_court = MiniCourt(video_frames[0])
    ball_shot_frames = ball_tracker.get_ball_shot_frames(ball_detections)

    # Convert to mini court coordinates
    player_mini_detections, ball_mini_detections = mini_court.convert_bounding_boxes_to_mini_court_coordinates(
        player_detections, ball_detections, court_keypoints)

    player_stats_data = [{
        'frame_num': 0,
        'player_1_number_of_shots': 0,
        'player_1_total_shot_speed': 0,
        'player_1_last_shot_speed': 0,
        'player_1_total_player_speed': 0,
        'player_1_last_player_speed': 0,

        'player_2_number_of_shots': 0,
        'player_2_total_shot_speed': 0,
        'player_2_last_shot_speed': 0,
        'player_2_total_player_speed': 0,
        'player_2_last_player_speed': 0,
    }]
    
    for ball_shot_ind in range(len(ball_shot_frames) - 1):
        start_frame = ball_shot_frames[ball_shot_ind]
        end_frame = ball_shot_frames[ball_shot_ind + 1]
        
        # FIX: Use actual fps here instead of hardcoded 24
        ball_shot_time = (end_frame - start_frame) / fps
        
        ball_distance_px = measure_distance(
            ball_mini_detections[start_frame][1],
            ball_mini_detections[end_frame][1]
        )
        ball_distance_m = convert_pixel_distance_to_meters(
            ball_distance_px,
            constants.DOUBLE_LINE_WIDTH,
            mini_court.get_width_of_mini_court()
        )
        ball_speed = (ball_distance_m / ball_shot_time) * 3.6  # km/h

        player_positions = player_mini_detections[start_frame]
        player_shot_ball = min(player_positions.keys(), key=lambda pid: measure_distance(
            player_positions[pid], ball_mini_detections[start_frame][1]))

        opponent_id = 1 if player_shot_ball == 2 else 2
        opp_distance_px = measure_distance(
            player_mini_detections[start_frame][opponent_id],
            player_mini_detections[end_frame][opponent_id]
        )
        opp_distance_m = convert_pixel_distance_to_meters(
            opp_distance_px,
            constants.DOUBLE_LINE_WIDTH,
            mini_court.get_width_of_mini_court()
        )
        opp_speed = (opp_distance_m / ball_shot_time) * 3.6

        stats = deepcopy(player_stats_data[-1])
        stats['frame_num'] = start_frame
        stats[f'player_{player_shot_ball}_number_of_shots'] += 1
        stats[f'player_{player_shot_ball}_total_shot_speed'] += ball_speed
        stats[f'player_{player_shot_ball}_last_shot_speed'] = ball_speed

        stats[f'player_{opponent_id}_total_player_speed'] += opp_speed
        stats[f'player_{opponent_id}_last_player_speed'] = opp_speed

        player_stats_data.append(stats)

    df_stats = pd.DataFrame(player_stats_data)
    frames_df = pd.DataFrame({'frame_num': list(range(len(video_frames)))})
    df_stats = pd.merge(frames_df, df_stats, on='frame_num', how='left').ffill()

    df_stats['player_1_average_shot_speed'] = df_stats['player_1_total_shot_speed'] / \
        df_stats['player_1_number_of_shots']
    df_stats['player_2_average_shot_speed'] = df_stats['player_2_total_shot_speed'] / \
        df_stats['player_2_number_of_shots']
    df_stats['player_1_average_player_speed'] = df_stats['player_1_total_player_speed'] / \
        df_stats['player_2_number_of_shots']
    df_stats['player_2_average_player_speed'] = df_stats['player_2_total_player_speed'] / \
        df_stats['player_1_number_of_shots']

    # Visual Output
    output_frames = player_tracker.draw_bboxes(video_frames, player_detections)
    output_frames = ball_tracker.draw_bboxes(output_frames, ball_detections)
    output_frames = court_line_detector.draw_keypoints_on_video(
        output_frames, court_keypoints)
    output_frames = mini_court.draw_mini_court(output_frames)
    output_frames = mini_court.draw_points_on_mini_court(
        output_frames, player_mini_detections)
    output_frames = mini_court.draw_points_on_mini_court(
        output_frames, ball_mini_detections, color=(0, 255, 255))
    output_frames = draw_player_stats(output_frames, df_stats)
    
    print(f"Total frames to save: {len(output_frames)}")
    
    # Debug prints
    print(f"Total frames: {len(output_frames)}")
    if len(output_frames) > 0:
        print(f"Frame size: {output_frames[0].shape}, dtype: {output_frames[0].dtype}")
    else:
        print("No frames found to save!")
        return None
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_video_path), exist_ok=True)
    
    # FIX: Use improved save_video function with H264 codec
    success = save_video_h264(output_frames, output_video_path, fps=fps)
    
    if success:
        return output_video_path
    else:
        print("❌ Failed to save video")
        return None


def save_video_h264(output_video_frames, output_video_path, fps=24):
    """
    Save video frames with H264 codec for Streamlit compatibility
    """
    if not output_video_frames:
        print("❌ No frames to save")
        return False
    
    # Get frame dimensions
    height, width, channels = output_video_frames[0].shape
    
    # Try different codec options for better compatibility
    codecs_to_try = [
        cv2.VideoWriter_fourcc(*'H264'),  # H264 - best for web
        cv2.VideoWriter_fourcc(*'X264'),  # X264 alternative
        cv2.VideoWriter_fourcc(*'mp4v'),  # Fallback
        cv2.VideoWriter_fourcc(*'XVID'),  # Last resort
    ]
    
    for codec in codecs_to_try:
        try:
            # Create VideoWriter object
            out = cv2.VideoWriter(output_video_path, codec, fps, (width, height))
            
            if not out.isOpened():
                print(f"❌ Failed to open VideoWriter with codec: {codec}")
                continue
            
            print(f"✅ Using codec: {codec}")
            print(f"📹 Saving {len(output_video_frames)} frames at {fps} fps")
            print(f"📐 Frame size: {width}x{height}")
            
            # Write frames
            for i, frame in enumerate(output_video_frames):
                if frame is None:
                    print(f"⚠️  Warning: Frame {i} is None, skipping")
                    continue
                
                # Ensure frame is in correct format
                if frame.dtype != 'uint8':
                    frame = frame.astype('uint8')
                
                # Ensure frame has correct dimensions
                if frame.shape != (height, width, channels):
                    print(f"⚠️  Warning: Frame {i} has wrong dimensions: {frame.shape}")
                    continue
                
                out.write(frame)
                
                # Progress indicator
                if i % 50 == 0:
                    print(f"📝 Written {i}/{len(output_video_frames)} frames")
            
            # Release the VideoWriter
            out.release()
            
            # Verify the output file exists and has content
            if os.path.exists(output_video_path):
                file_size = os.path.getsize(output_video_path)
                print(f"📁 Video saved: {output_video_path}")
                print(f"📊 File size: {file_size / (1024*1024):.2f} MB")
                
                if file_size > 0:
                    return True
                else:
                    print("❌ Output file is empty")
            else:
                print("❌ Output file was not created")
                
        except Exception as e:
            print(f"❌ Error with codec {codec}: {e}")
            continue
    
    print("❌ All codecs failed")
    return False


if __name__ == "__main__":
    default_input = "input_videos/input_video.mp4"
    default_output = "output_videos/output_video.mp4"
    run_analysis(default_input, default_output)