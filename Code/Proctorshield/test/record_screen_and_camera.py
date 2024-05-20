import cv2
import numpy as np
import pyautogui
import argparse
import os

# Function to merge screen recording and camera feed
def merge_frames(screen_frame, camera_frame):
    screen_frame = cv2.resize(screen_frame, (640, 480))
    camera_frame = cv2.resize(camera_frame, (640, 480))
    return np.hstack((screen_frame, camera_frame))

# Function to record screen and camera feed
def record_screen_and_camera(output_file):
    # Video writer for saving the output
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_file, fourcc, 20.0, (1280, 480))

    # Record the screen and camera feed
    while True:
        # Capture screen
        screen_frame = pyautogui.screenshot()
        screen_frame = cv2.cvtColor(np.array(screen_frame), cv2.COLOR_RGB2BGR)

        # Capture camera feed
        ret, camera_frame = camera.read()
        if not ret:
            break

        # Merge frames
        merged_frame = merge_frames(screen_frame, camera_frame)

        # Write merged frame to output video
        out.write(merged_frame)

        # Display merged frame
        cv2.imshow('Recording', merged_frame)

        # Break the loop when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    out.release()
    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Argument parser
    parser = argparse.ArgumentParser(description="Record screen and camera feed")
    parser.add_argument("-o", "--output", type=str, default="output.mp4", help="Output file path")
    args = parser.parse_args()

    # Create directory if it doesn't exist
    output_directory = os.path.dirname(args.output)
    if output_directory and not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # OpenCV camera capture
    camera = cv2.VideoCapture(0)

    # Record screen and camera feed
    record_screen_and_camera(args.output)
