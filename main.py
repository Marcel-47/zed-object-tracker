import sys
from datetime import datetime
import cv2
import pyzed.sl as sl
import numpy as np
from detector.zed_detector import ZEDDetector
from detector.zed_detector import TargetPosition
from visualizer.visualizer import draw


def select_closest(targets: list[TargetPosition]) -> TargetPosition | None:
    if not targets:
        return None
    return min(targets, key=lambda t: t.z)


def format_terminal_output(selected: TargetPosition | None) -> str:
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    if selected is None:
        return f"[{ts}] No ball detected"
    x_label = "right" if selected.x >= 0 else "left"
    y_label = "up" if selected.y >= 0 else "down"
    z_label = "away" if selected.z >= 0 else "towards"
    return (
        f"[{ts}] Ball detected | "
        f"X: {selected.x:+.2f}m ({x_label}) | "
        f"Y: {selected.y:+.2f}m ({y_label}) | "
        f"Z: {selected.z:+.2f}m ({z_label})"
    )

def main():
    # Create a Camera object
    zed = sl.Camera()

    # Create a InitParameters object and set configuration parameters
    init_params = sl.InitParameters()
    init_params.depth_mode = sl.DEPTH_MODE.NEURAL
    init_params.coordinate_units = sl.UNIT.METER
    init_params.sdk_verbose = 1

    # Open the camera
    err = zed.open(init_params)
    if err > sl.ERROR_CODE.SUCCESS:
        print("Camera Open : "+repr(err)+". Exit program.")
        exit()

    obj_param = sl.ObjectDetectionParameters()
    obj_param.enable_tracking = True       # keeps object IDs stable across frames
    obj_param.enable_segmentation = False   # provides per-object pixel masks (disable to reduce CPU load)
    # MEDIUM balances speed and accuracy; switch to MULTI_CLASS_BOX_ACCURATE for better detection at the cost of performance and speed
    obj_param.detection_model = sl.OBJECT_DETECTION_MODEL.MULTI_CLASS_BOX_ACCURATE

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
        exit()

    detector = ZEDDetector()
    image = sl.Mat()
    objects = sl.Objects()
    obj_runtime_param = sl.ObjectDetectionRuntimeParameters()
    # Minimum confidence (0–100) for a detection to be reported.
    # Lower values catch more objects but increase false positives; raise to filter noise.
    obj_runtime_param.detection_confidence_threshold = 15  # Adjust based on your environment and needs
    zed.set_object_detection_runtime_parameters(obj_runtime_param)  # can be updated mid-run

    print("Tracking started. Press 'q' to quit.")

    while True:
        if zed.grab() != sl.ERROR_CODE.SUCCESS:
            continue

        zed.retrieve_image(image, sl.VIEW.LEFT)
        zed.retrieve_objects(objects, obj_runtime_param)

        frame = cv2.cvtColor(image.get_data(), cv2.COLOR_BGRA2BGR)
        all_targets = detector.get_all_target_positions(frame, objects)
        selected = select_closest(all_targets)

        annotated = draw(frame, all_targets, selected)
        label = "Press 'q' to quit"
        (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.putText(annotated, label, (annotated.shape[1] - w - 10, h + 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.imshow("ZED Tennis Ball Tracker", annotated)
        print(format_terminal_output(selected))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Close the camera
    zed.disable_object_detection()
    zed.close()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()