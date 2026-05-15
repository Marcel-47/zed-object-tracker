from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any
import numpy as np
import pyzed.sl as sl


@dataclass
class TargetPosition:
    """Holds the detected position and size of one target in a single frame."""
    x: float           # left/right position in meters (camera coordinate system)
    y: float           # up/down position in meters
    z: float           # distance from camera in meters
    confidence: float  # detection confidence between 0.0 (low) and 1.0 (high)
    bbox: tuple[int, int, int, int]  # bounding box as (x1, y1, x2, y2) in pixels


class Detector(ABC):
    """Base class for all detector implementations."""
    @abstractmethod
    def get_targets(self, frame: Any, objects: Any) -> list[TargetPosition]:
        """Detect all targets in the current frame and return their positions."""
        ...


class ZEDDetector(Detector):
    def get_targets(self, _frame, objects) -> list[TargetPosition]:
        results = []
        for obj in objects.object_list:
            if obj.label != sl.OBJECT_CLASS.SPORT:
                continue
            x, y, z = float(obj.position[0]), float(obj.position[1]), float(obj.position[2])
            confidence = float(obj.confidence) / 100.0
            bbox_corners = obj.bounding_box_2d
            x1 = int(bbox_corners[0][0])
            y1 = int(bbox_corners[0][1])
            x2 = int(bbox_corners[2][0])
            y2 = int(bbox_corners[2][1])
            results.append(TargetPosition(x=x, y=y, z=z, confidence=confidence, bbox=(x1, y1, x2, y2)))
        return results
