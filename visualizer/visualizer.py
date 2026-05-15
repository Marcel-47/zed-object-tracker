import cv2
import numpy as np
from detector.zed_detector import TargetPosition


GREEN_DIM = (0, 120, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 200)
FONT = cv2.FONT_HERSHEY_SIMPLEX

def draw(frame, all_targets, selected):
    out = frame.copy()

    for target in all_targets:
        x1, y1, x2, y2 = target.bbox
        cv2.rectangle(out, (x1, y1), (x2, y2), GREEN_DIM, 1)

    if selected is None:
        cv2.putText(out, "No targets detected", (10, 30), FONT, 0.7, RED, 2)
        return out

    # Draw a bright box around the closest target
    x1, y1, x2, y2 = selected.bbox
    cv2.rectangle(out, (x1, y1), (x2, y2), GREEN, 2)

    # Build the label line by line so it's easy to read
    x_dir = "right" if selected.x >= 0 else "left"
    y_dir = "up"    if selected.y >= 0 else "down"
    z_dir = "away"  if selected.z >= 0 else "towards"
    label = f"X:{selected.x:+.2f}m ({x_dir})  Y:{selected.y:+.2f}m ({y_dir})  Z:{selected.z:+.2f}m ({z_dir})"

    text_y = max(y1 - 8, 15)  # keep text on screen if box is near the top
    cv2.putText(out, label, (x1, text_y), FONT, 0.5, GREEN, 1)

    return out