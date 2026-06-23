import sys
import argparse
import time
from collections import deque
from datetime import datetime
import cv2
import pyzed.sl as sl
import numpy as np
from config import load_config, run_configure
from detector.zed_detector import ZEDDetector
from detector.zed_detector import TargetPosition
from visualizer.visualizer import draw


def format_terminal_output(all_targets: list[TargetPosition], id_to_num: dict[int, int], selected_num: int | None) -> str:
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    if not all_targets:
        return f"[{ts}] No object detected"
    lines = [f"[{ts}] {len(all_targets)} object(s) detected:"]
    for t in all_targets:
        num = id_to_num.get(t.track_id, "?")
        x_label = "right" if t.x >= 0 else "left"
        y_label = "up" if t.y >= 0 else "down"
        z_label = "away" if t.z >= 0 else "towards"
        marker = " [selected]" if num == selected_num else ""
        lines.append(
            f"  #{num}{marker} | "
            f"X: {t.x:+.2f}m ({x_label}) | "
            f"Y: {t.y:+.2f}m ({y_label}) | "
            f"Z: {t.z:+.2f}m ({z_label})"
        )
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--configure", action="store_true", help="Edit config.json interactively before starting")
    args = parser.parse_args()
    if args.configure:
        run_configure()

    cfg = load_config()

    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = cfg["depth_mode"]
    init_params.coordinate_units = cfg["coordinate_units"]
    init_params.sdk_verbose = cfg["sdk_verbose"]

    # Open the camera
    err = zed.open(init_params)
    if err > sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(err)+". Exit program.")
        sys.exit(1)

    obj_param = sl.ObjectDetectionParameters()
    obj_param.enable_tracking = cfg["enable_tracking"]       # keeps object IDs stable across frames
    obj_param.enable_segmentation = cfg["enable_segmentation"]   # provides per-object pixel masks (disable to reduce CPU load)
    # MEDIUM balances speed and accuracy; switch to MULTI_CLASS_BOX_ACCURATE for better detection at the cost of performance and speed
    obj_param.detection_model = cfg["detection_model"]

    if obj_param.enable_tracking:
        positional_tracking_param = sl.PositionalTrackingParameters()
        # set_as_static = True would disable camera motion estimation (only use if camera is fixed)
        #positional_tracking_param.set_as_static = True
        zed.enable_positional_tracking(positional_tracking_param)

    print("Object Detection: Loading Module...")

    err = zed.enable_object_detection(obj_param)
    if err != sl.ERROR_CODE.SUCCESS:
        print("Enable object detection : "+repr(err)+". Exit program.")
        zed.close()
        sys.exit(1)

    detector = ZEDDetector(cfg["object_class"])
    image = sl.Mat()
    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    # Minimum confidence (0–100) for a detection to be reported.
    # Lower values catch more objects but increase false positives; raise to filter noise.
    obj_runtime_param.detection_confidence_threshold = cfg["detection_confidence_threshold"]  # Adjust based on your environment and needs - lower for more detections, higher to reduce false positives
    zed.set_object_detection_runtime_parameters(obj_runtime_param)  # can be updated mid-run

    print("Tracking started. Press a number key to select an object, '0' to deselect, 'q' to quit.")

    COLOR_CYCLE = ["", "blue", "red", "green", "yellow", "orange", "purple"]

    id_to_num: dict[int, int] = {}
    selected_num: int | None = None
    input_buffer: str = ""
    show_overlay: bool = True
    auto_select: bool = False
    color_filter_idx: int = 0
    last_print_time = 0.0
    hint_label = "Type number + Enter to select | '0' + Enter to deselect | Esc to cancel | 'r' to reset | 'h' overlay | 'c' auto-select | 'f' color filter | 'q' to quit"
    (hint_w, hint_h), _ = cv2.getTextSize(hint_label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
    frame_times: deque = deque(maxlen=30)
    last_frame_time = time.monotonic()
    consecutive_grab_failures = 0
    window_name = "ZED Object Tracker"

    try:
        while True:
            if zed.grab() != sl.ERROR_CODE.SUCCESS:
                consecutive_grab_failures += 1
                if consecutive_grab_failures >= 30:
                    print("Camera lost: too many consecutive grab failures. Exiting.")
                    break
                continue
            consecutive_grab_failures = 0

            now = time.monotonic()
            frame_times.append(now - last_frame_time)
            last_frame_time = now
            total = sum(frame_times)
            fps = len(frame_times) / total if total > 0 else None

            zed.retrieve_image(image, sl.VIEW.LEFT)
            zed.retrieve_objects(objects, obj_runtime_param)

            frame = cv2.cvtColor(image.get_data(), cv2.COLOR_BGRA2BGR)
            detector.color_filter = COLOR_CYCLE[color_filter_idx]
            all_targets = detector.get_all_target_positions(frame, objects)

            current_ids = {t.track_id for t in all_targets}
            for gone in list(id_to_num):
                if gone not in current_ids:
                    del id_to_num[gone]
            for t in all_targets:
                if t.track_id not in id_to_num:
                    used = set(id_to_num.values())
                    id_to_num[t.track_id] = next(n for n in range(1, len(used) + 2) if n not in used)
            if selected_num not in id_to_num.values():
                selected_num = None

            if auto_select and all_targets:
                closest = min(all_targets, key=lambda t: t.z)
                selected_num = id_to_num.get(closest.track_id)

            annotated = draw(frame, all_targets, id_to_num, selected_num, fps=fps, input_buffer=input_buffer, show_overlay=show_overlay, auto_select=auto_select, color_filter=COLOR_CYCLE[color_filter_idx])
            cv2.putText(annotated, hint_label, (annotated.shape[1] - hint_w - 10, hint_h + 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
            cv2.imshow(window_name, annotated)
            if now - last_print_time >= 1.0:
                print(format_terminal_output(all_targets, id_to_num, selected_num))
                last_print_time = now

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
            elif key == 13:  # Enter
                if input_buffer:
                    n = int(input_buffer)
                    selected_num = None if n == 0 else n
                    input_buffer = ""
                    auto_select = False
            elif key == 27:  # Escape
                input_buffer = ""
            elif key == ord('r'):
                id_to_num.clear()
                selected_num = None
                input_buffer = ""
                show_overlay = True
                auto_select = False
                color_filter_idx = 0
            elif key == ord('h'):
                show_overlay = not show_overlay
            elif key == ord('f'):
                color_filter_idx = (color_filter_idx + 1) % len(COLOR_CYCLE)
            elif key == ord('c'):
                auto_select = not auto_select
            elif key == 8:  # Backspace
                input_buffer = input_buffer[:-1]
            elif ord('0') <= key <= ord('9'):
                input_buffer += chr(key)
    finally:
        # Always release the camera, even on Ctrl+C or an unexpected error,
        # so the ZED is not left open (which can require a physical replug).
        zed.disable_object_detection()
        zed.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()