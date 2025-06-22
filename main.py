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


def main():
    input_video_path = os.path.abspath("input_videos/input_video.mp4")
    video_frames = read_video(input_video_path)
    # Read Video
    input_video_path = "input_videos/input_video.mp4"
    video_frames = read_video(input_video_path)
    if not video_frames:
        print(f"❌ Error: No frames found. Check if '{input_video_path}' exists and is readable.")
        return

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
        ball_shot_time = (end_frame - start_frame) / 24  # fps = 24

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

    for i, frame in enumerate(output_frames):
        cv2.putText(frame, f"Frame: {i}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
    # Make sure output directory exists
    output_path = "output_videos/output_video.mp4"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    save_video(output_frames, output_path)
  


    # save_video(output_frames, "output_videos/output_video.avi")


if __name__ == "__main__":
    main()
