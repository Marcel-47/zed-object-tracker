from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import math
import numpy as np
import cv2
import pyzed.sl as sl


# HSV color ranges for the color filter.
# Each entry is a list of (h_lo, s_lo, v_lo, h_hi, s_hi, v_hi) tuples.
# Red needs two entries because hue wraps around at 0/179 on the color wheel.
# Hue boundaries are the same for both lighting presets; only the saturation
# and value floors change. Indoor light is dimmer, so colors read less
# saturated and darker and need lower floors. Outdoor light is brighter, so the
# floors are raised to reject sun-washed, pale background. The outdoor floors
# are seed values to refine on-site, the same way the indoor floors were tuned.
_COLOR_RANGES_INDOOR = {
    "blue":   [(100, 80, 50, 130, 255, 255)],
    "red":    [(0,   60, 40,  10, 255, 255),
               (160, 60, 40, 179, 255, 255)],
    "green":  [(35,  60, 40,  85, 255, 255)],
    "yellow": [(25,  80, 50,  35, 255, 255)],
    "orange": [(10,  80, 50,  25, 255, 255)],
    "purple": [(130, 80, 50, 160, 255, 255)],
}

_COLOR_RANGES_OUTDOOR = {
    "blue":   [(100, 110, 80, 130, 255, 255)],
    "red":    [(0,    90, 70,  10, 255, 255),
               (160,  90, 70, 179, 255, 255)],
    "green":  [(35,   90, 70,  85, 255, 255)],
    "yellow": [(25,  110, 80,  35, 255, 255)],
    "orange": [(10,  110, 80,  25, 255, 255)],
    "purple": [(130, 110, 80, 160, 255, 255)],
}

_COLOR_RANGES_BY_LIGHTING = {
    "indoor":  _COLOR_RANGES_INDOOR,
    "outdoor": _COLOR_RANGES_OUTDOOR,
}


@dataclass
class TargetPosition:
    """Holds the detected position and size of one target in a single frame."""
    x: float           # left/right position in meters (camera coordinate system)
    y: float           # up/down position in meters
    z: float           # distance from camera in meters
    confidence: float  # detection confidence between 0.0 (low) and 1.0 (high)
    bbox: tuple[int, int, int, int]  # bounding box as (x1, y1, x2, y2) in pixels
    track_id: int = 0  # stable ID assigned by the ZED SDK tracker


class Detector(ABC):
    """Base class for all detector implementations."""
    @abstractmethod
    def get_all_target_positions(self, frame: Any, objects: Any) -> list[TargetPosition]:
        """Detect all targets in the current frame and return their positions."""
        ...


class ZEDDetector(Detector):
    """
    Detects objects in each ZED camera frame using the ZED SDK's built-in object detection.

    The ZED SDK runs a multi-class model that detects all supported object classes
    simultaneously. This class filters those results down to only the classes you
    care about and converts them into TargetPosition objects.

    What you can customize:
    - Which object class(es) to track: pass an sl.OBJECT_CLASS value to __init__.
      Available classes: sl.OBJECT_CLASS.PERSON, VEHICLE, BAG, ANIMAL,
      ELECTRONICS, FRUIT_VEGETABLE, SPORT. Configured via config.json.
    - Detection confidence threshold: set in main.py via
      obj_runtime_param.detection_confidence_threshold (0–100).
      Lower = more detections, higher = fewer false positives.
    - Detection model accuracy vs. speed: set in main.py via
      obj_param.detection_model. Use MULTI_CLASS_BOX_ACCURATE for better accuracy
      or MULTI_CLASS_BOX_MEDIUM or MULTI_CLASS_BOX_FAST for higher frame rate.
    - Color filter: set self.color_filter to a key from the active color ranges
      at runtime. Objects whose bounding box does not contain enough of that
      color are discarded.
    - Lighting preset: pass "indoor" or "outdoor" to __init__ to pick the
      saturation/value floors the color filter uses. Configured via config.json.
    """

    def __init__(self, object_class=sl.OBJECT_CLASS.FRUIT_VEGETABLE, lighting: str = "indoor", color_match_threshold: float = 0.15):
        self.object_class = object_class
        self.color_filter: str = ""
        self.color_match_threshold = color_match_threshold
        self._color_ranges = _COLOR_RANGES_BY_LIGHTING.get(lighting, _COLOR_RANGES_INDOOR)

    def get_all_target_positions(self, frame, objects) -> list[TargetPosition]:
        results = []
        for obj in objects.object_list:
            if obj.label != self.object_class:
                continue
            # The ZED SDK's default IMAGE coordinate system has +Y pointing down;
            # negate it so +Y means up for the rest of the pipeline.
            x, y, z = float(obj.position[0]), -float(obj.position[1]), float(obj.position[2])
            if not (math.isfinite(x) and math.isfinite(y) and math.isfinite(z)):
                continue
            confidence = float(obj.confidence) / 100.0
            bbox_corners = obj.bounding_box_2d
            x1 = int(bbox_corners[0][0])
            y1 = int(bbox_corners[0][1])
            x2 = int(bbox_corners[2][0])
            y2 = int(bbox_corners[2][1])

            if self.color_filter in self._color_ranges:
                region = frame[y1:y2, x1:x2]
                if region.size > 0:
                    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
                    combined = np.zeros(hsv.shape[:2], dtype=np.uint8)
                    for (hl, sl_, vl, hh, sh, vh) in self._color_ranges[self.color_filter]:
                        combined = cv2.bitwise_or(combined, cv2.inRange(hsv, (hl, sl_, vl), (hh, sh, vh)))
                    if combined.mean() / 255 < self.color_match_threshold:
                        continue

            results.append(TargetPosition(x=x, y=y, z=z, confidence=confidence, bbox=(x1, y1, x2, y2), track_id=int(obj.id)))
        return results
