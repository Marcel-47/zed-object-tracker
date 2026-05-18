import cv2

GREEN  = (0, 190, 0)
RED    = (0, 0, 220)
ORANGE = (0, 165, 255)
FONT   = cv2.FONT_HERSHEY_SIMPLEX

CONF_BAR_H   = 4    # height of confidence bar below each bounding box in pixels
CROSSHAIR_R  = 8    # half-length of crosshair arms in pixels

_MAP_W       = 180  # top-down map width in pixels
_MAP_H       = 150  # top-down map height in pixels
_MAP_X_RANGE = 2.0  # meters from center to left/right edge
_MAP_Z_RANGE = 5.0  # max depth shown in meters


def _pos_label(target) -> str:
    x_dir = "right" if target.x >= 0 else "left"
    y_dir = "up"    if target.y >= 0 else "down"
    z_dir = "away"  if target.z >= 0 else "towards"
    return f"X:{target.x:+.2f}m ({x_dir})  Y:{target.y:+.2f}m ({y_dir})  Z:{target.z:+.2f}m ({z_dir})"


def draw(frame, all_targets, id_to_num: dict, selected_num: int | None, fps=None, proximity_threshold=None):
    out = frame.copy()
    frame_h, frame_w = out.shape[:2]

    # --- Per-object overlays ---
    if not all_targets:
        msg = "No objects detected"
        (msg_w, _), _ = cv2.getTextSize(msg, FONT, 0.7, 2)
        cv2.putText(out, msg, (frame_w - msg_w - 10, frame_h - 10), FONT, 0.7, RED, 2)
    else:
        for target in all_targets:
            num = id_to_num.get(target.track_id)
            is_selected = num is not None and num == selected_num
            is_close = proximity_threshold is not None and target.z < proximity_threshold
            if is_selected:
                color = RED
            elif is_close:
                color = ORANGE
            else:
                color = GREEN

            x1, y1, x2, y2 = target.bbox
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

            # Number badge in the top-left corner of the box
            num_label = f"#{num}" if num is not None else "?"
            cv2.putText(out, num_label, (x1 + 4, y1 + 18), FONT, 0.6, color, 2)

            # Position info just above the box
            text_y = max(y1 - 8, 15)
            cv2.putText(out, _pos_label(target), (x1, text_y), FONT, 0.45, color, 1)

            # Crosshair at bbox center
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.line(out, (cx - CROSSHAIR_R, cy), (cx + CROSSHAIR_R, cy), color, 1)
            cv2.line(out, (cx, cy - CROSSHAIR_R), (cx, cy + CROSSHAIR_R), color, 1)

            # Confidence bar just below the box
            bar_y0, bar_y1 = y2 + 2, y2 + 2 + CONF_BAR_H
            cv2.rectangle(out, (x1, bar_y0), (x2, bar_y1), (60, 60, 60), -1)
            cv2.rectangle(out, (x1, bar_y0), (x1 + int((x2 - x1) * target.confidence), bar_y1), color, -1)

            if is_close:
                cv2.putText(out, "CLOSE", (x1, bar_y1 + 14), FONT, 0.45, ORANGE, 1)

    # --- HUD: FPS and object count (top-left) ---
    hud_y = 25
    if fps is not None:
        cv2.putText(out, f"FPS: {fps:.1f}", (10, hud_y), FONT, 0.55, (255, 255, 255), 1)
        hud_y += 22
    cv2.putText(out, f"Objects: {len(all_targets)}", (10, hud_y), FONT, 0.55, (255, 255, 255), 1)

    # --- Top-down position map (bottom-left) ---
    mx, my = 10, frame_h - _MAP_H - 10
    cv2.rectangle(out, (mx, my), (mx + _MAP_W, my + _MAP_H), (30, 30, 30), -1)
    cv2.rectangle(out, (mx, my), (mx + _MAP_W, my + _MAP_H), (100, 100, 100), 1)
    # Camera dot at bottom-center of the map
    cv2.circle(out, (mx + _MAP_W // 2, my + _MAP_H - 6), 4, (200, 200, 200), -1)
    cv2.putText(out, "L", (mx + 3, my + _MAP_H - 4), FONT, 0.3, (150, 150, 150), 1)
    cv2.putText(out, "R", (mx + _MAP_W - 10, my + _MAP_H - 4), FONT, 0.3, (150, 150, 150), 1)
    for target in all_targets:
        num = id_to_num.get(target.track_id)
        is_selected = num is not None and num == selected_num
        is_close = proximity_threshold is not None and target.z < proximity_threshold
        dot_color = RED if is_selected else (ORANGE if is_close else GREEN)
        dot_x = mx + _MAP_W // 2 + int((target.x / _MAP_X_RANGE) * (_MAP_W // 2))
        dot_y = my + _MAP_H - 6 - int((target.z / _MAP_Z_RANGE) * (_MAP_H - 12))
        dot_x = max(mx + 3, min(mx + _MAP_W - 3, dot_x))
        dot_y = max(my + 3, min(my + _MAP_H - 3, dot_y))
        cv2.circle(out, (dot_x, dot_y), 4, dot_color, -1)

    return out
