import cv2


GREEN_DIM = (0, 190, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 200)
FONT = cv2.FONT_HERSHEY_SIMPLEX

def _label(target) -> str:
    x_dir = "right" if target.x >= 0 else "left"
    y_dir = "up"    if target.y >= 0 else "down"
    z_dir = "away"  if target.z >= 0 else "towards"
    return f"X:{target.x:+.2f}m ({x_dir})  Y:{target.y:+.2f}m ({y_dir})  Z:{target.z:+.2f}m ({z_dir})"


def draw(frame, all_targets, selected):
    out = frame.copy()

    if not all_targets:
        cv2.putText(out, "No targets detected", (10, 30), FONT, 0.7, RED, 2)
        return out

    for target in all_targets:
        x1, y1, x2, y2 = target.bbox
        is_closest = selected is not None and target is selected
        color = GREEN if is_closest else GREEN_DIM
        thickness = 2 if is_closest else 1
        cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness)
        text_y = max(y1 - 8, 15)
        cv2.putText(out, _label(target), (x1, text_y), FONT, 0.5, color, 1)

    return out