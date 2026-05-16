import cv2

GREEN = (0, 190, 0)
RED = (0, 0, 220)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def _pos_label(target) -> str:
    x_dir = "right" if target.x >= 0 else "left"
    y_dir = "up"    if target.y >= 0 else "down"
    z_dir = "away"  if target.z >= 0 else "towards"
    return f"X:{target.x:+.2f}m ({x_dir})  Y:{target.y:+.2f}m ({y_dir})  Z:{target.z:+.2f}m ({z_dir})"


def draw(frame, all_targets, id_to_num: dict, selected_num: int | None):
    out = frame.copy()

    if not all_targets:
        cv2.putText(out, "No targets detected", (10, 30), FONT, 0.7, RED, 2)
        return out

    for target in all_targets:
        num = id_to_num.get(target.track_id)
        is_selected = num is not None and num == selected_num
        color = RED if is_selected else GREEN

        x1, y1, x2, y2 = target.bbox
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

        # Number badge in the top-left corner of the box
        num_label = f"#{num}" if num is not None else "?"
        cv2.putText(out, num_label, (x1 + 4, y1 + 18), FONT, 0.6, color, 2)

        # Position info just above the box
        text_y = max(y1 - 8, 15)
        cv2.putText(out, _pos_label(target), (x1, text_y), FONT, 0.45, color, 1)

    return out
