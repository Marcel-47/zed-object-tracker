import json
import os
import pyzed.sl as sl

# Valid values for "depth_mode" in config.json.
# PERFORMANCE: fastest, lowest accuracy
# QUALITY:     balanced
# ULTRA:       slower, higher accuracy
# NEURAL:      AI-based, good accuracy at moderate cost (default)
# NEURAL_PLUS: highest accuracy, most compute-intensive
DEPTH_MODE_MAP = {
    "PERFORMANCE": sl.DEPTH_MODE.PERFORMANCE,
    "QUALITY":     sl.DEPTH_MODE.QUALITY,
    "ULTRA":       sl.DEPTH_MODE.ULTRA,
    "NEURAL":      sl.DEPTH_MODE.NEURAL,
    "NEURAL_PLUS": sl.DEPTH_MODE.NEURAL_PLUS,
}

# Valid values for "coordinate_units" in config.json.
# All x/y/z position values in TargetPosition will be expressed in this unit.
UNIT_MAP = {
    "MILLIMETER": sl.UNIT.MILLIMETER,
    "CENTIMETER": sl.UNIT.CENTIMETER,
    "METER":      sl.UNIT.METER,       # default
    "INCH":       sl.UNIT.INCH,
    "FOOT":       sl.UNIT.FOOT,
}

# Valid values for "detection_model" in config.json.
# FAST:     highest FPS, lowest accuracy — use on heavily load-limited hardware
# MEDIUM:   balanced speed and accuracy
# ACCURATE: best detection quality, most compute-intensive (default)
DETECTION_MODEL_MAP = {
    "MULTI_CLASS_BOX_FAST":     sl.OBJECT_DETECTION_MODEL.MULTI_CLASS_BOX_FAST,
    "MULTI_CLASS_BOX_MEDIUM":   sl.OBJECT_DETECTION_MODEL.MULTI_CLASS_BOX_MEDIUM,
    "MULTI_CLASS_BOX_ACCURATE": sl.OBJECT_DETECTION_MODEL.MULTI_CLASS_BOX_ACCURATE,
}

# Valid values for "object_class" in config.json.
# Tennis balls are classified as FRUIT_VEGETABLE by the ZED multi-class model.
OBJECT_CLASS_MAP = {
    "PERSON":          sl.OBJECT_CLASS.PERSON,
    "VEHICLE":         sl.OBJECT_CLASS.VEHICLE,
    "BAG":             sl.OBJECT_CLASS.BAG,
    "ANIMAL":          sl.OBJECT_CLASS.ANIMAL,
    "ELECTRONICS":     sl.OBJECT_CLASS.ELECTRONICS,
    "FRUIT_VEGETABLE": sl.OBJECT_CLASS.FRUIT_VEGETABLE,  # default — covers tennis balls
    "SPORT":           sl.OBJECT_CLASS.SPORT,
}

_DEFAULTS = {
    "depth_mode":                    "NEURAL",           # see DEPTH_MODE_MAP for valid values
    "coordinate_units":              "METER",            # see UNIT_MAP for valid values
    "sdk_verbose":                   1,                  # 0 = silent, 1 = verbose SDK logging
    "enable_tracking":               True,               # keeps object IDs stable across frames
    "enable_segmentation":           False,              # per-object pixel masks; disable to reduce CPU load
    "detection_model":               "MULTI_CLASS_BOX_ACCURATE",  # see DETECTION_MODEL_MAP for valid values
    "detection_confidence_threshold": 40,                # 0–100; lower catches more objects but increases false positives
    "object_class":                  "FRUIT_VEGETABLE",  # see OBJECT_CLASS_MAP for valid values
}


def load_config(path="config.json"):
    cfg = dict(_DEFAULTS)
    if os.path.exists(path):
        with open(path) as f:
            cfg.update(json.load(f))
    return {
        "depth_mode":                    DEPTH_MODE_MAP[cfg["depth_mode"]],
        "coordinate_units":              UNIT_MAP[cfg["coordinate_units"]],
        "sdk_verbose":                   int(cfg["sdk_verbose"]),
        "enable_tracking":               bool(cfg["enable_tracking"]),
        "enable_segmentation":           bool(cfg["enable_segmentation"]),
        "detection_model":               DETECTION_MODEL_MAP[cfg["detection_model"]],
        "detection_confidence_threshold": int(cfg["detection_confidence_threshold"]),
        "object_class":                  OBJECT_CLASS_MAP[cfg["object_class"]],
    }
