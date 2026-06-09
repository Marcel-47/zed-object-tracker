import cv2

GREEN  = (0, 190, 0)
RED    = (0, 0, 220)
FONT   = cv2.FONT_HERSHEY_SIMPLEX

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


def draw(frame, all_targets, id_to_num: dict, selected_num: int | None, fps=None, input_buffer: str = "", show_overlay: bool = True, auto_select: bool = False, color_filter: str = ""):
    out = frame.copy()
    frame_h, frame_w = out.shape[:2]

    # --- Camera center crosshair (X=0, Y=0) ---
    cx, cy = frame_w // 2, frame_h // 2
    cv2.line(out, (cx - 20, cy), (cx + 20, cy), (55, 55, 55), 1)
    cv2.line(out, (cx, cy - 20), (cx, cy + 20), (55, 55, 55), 1)

    # --- Per-object overlays ---
    if not all_targets:
        msg = "No objects detected"
        (msg_w, _), _ = cv2.getTextSize(msg, FONT, 0.7, 2)
        cv2.putText(out, msg, (frame_w - msg_w - 10, frame_h - 10), FONT, 0.7, RED, 2)
    else:
        for target in all_targets:
            num = id_to_num.get(target.track_id)
            is_selected = num is not None and num == selected_num
            color = RED if is_selected else GREEN

            x1, y1, x2, y2 = target.bbox
            cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)

            if show_overlay:
                # Number badge in the top-left corner of the box
                num_label = f"#{num}" if num is not None else "?"
                cv2.putText(out, num_label, (x1 + 4, y1 + 18), FONT, 0.6, color, 2)

                # Confidence percentage in the top-right corner of the box
                conf_label = f"{int(target.confidence * 100)}%"
                (conf_w, _), _ = cv2.getTextSize(conf_label, FONT, 0.6, 2)
                cv2.putText(out, conf_label, (x2 - conf_w - 4, y1 + 18), FONT, 0.6, color, 2)

                # Position info just above the box
                text_y = max(y1 - 8, 15)
                cv2.putText(out, _pos_label(target), (x1, text_y), FONT, 0.45, color, 1)

            # Crosshair at bbox center
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.line(out, (cx - CROSSHAIR_R, cy), (cx + CROSSHAIR_R, cy), color, 1)
            cv2.line(out, (cx, cy - CROSSHAIR_R), (cx, cy + CROSSHAIR_R), color, 1)

    # --- HUD: FPS and object count (top-left) ---
    hud_y = 25
    if fps is not None:
        cv2.putText(out, f"FPS: {fps:.1f}", (10, hud_y), FONT, 0.55, (255, 255, 255), 1)
        hud_y += 22
    cv2.putText(out, f"Objects: {len(all_targets)}", (10, hud_y), FONT, 0.55, (255, 255, 255), 1)
    hud_y += 22
    if auto_select:
        cv2.putText(out, "AUTO", (10, hud_y), FONT, 0.55, (0, 200, 255), 1)
        hud_y += 22
    if color_filter:
        cv2.putText(out, f"COLOR: {color_filter.upper()}", (10, hud_y), FONT, 0.55, (255, 255, 255), 1)
        hud_y += 22
    if input_buffer:
        cv2.putText(out, f"> {input_buffer}_", (10, hud_y), FONT, 0.55, (255, 255, 0), 1)

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
        dot_color = RED if is_selected else GREEN
        dot_x = mx + _MAP_W // 2 + int((target.x / _MAP_X_RANGE) * (_MAP_W // 2))
        dot_y = my + _MAP_H - 6 - int((target.z / _MAP_Z_RANGE) * (_MAP_H - 12))
        dot_x = max(mx + 3, min(mx + _MAP_W - 3, dot_x))
        dot_y = max(my + 3, min(my + _MAP_H - 3, dot_y))
        cv2.circle(out, (dot_x, dot_y), 4, dot_color, -1)

    # --- Coordinate axis legend (bottom-right) ---
    legend_lines = ["X: right / left", "Y: up / down", "Z: away / towards"]
    legend_y = frame_h - 10
    for line in reversed(legend_lines):
        (lw, _), _ = cv2.getTextSize(line, FONT, 0.4, 1)
        cv2.putText(out, line, (frame_w - lw - 10, legend_y), FONT, 0.4, (150, 150, 150), 1)
        legend_y -= 16

    return out
