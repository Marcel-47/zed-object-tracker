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


# Drives the --configure prompt: (key, description, valid options or None for free integer 0-100)
_CONFIGURE_FIELDS = [
    ("depth_mode",                    "Depth estimation algorithm",            list(DEPTH_MODE_MAP)),
    ("coordinate_units",              "Unit for X/Y/Z position output",        list(UNIT_MAP)),
    ("sdk_verbose",                   "ZED SDK logging (0=silent, 1=verbose)", ["0", "1"]),
    ("enable_tracking",               "Stable object IDs across frames",       ["true", "false"]),
    ("enable_segmentation",           "Per-object pixel masks (costs CPU)",    ["true", "false"]),
    ("detection_model",               "Detection model quality vs. speed",     list(DETECTION_MODEL_MAP)),
    ("detection_confidence_threshold","Minimum detection confidence",          None),
    ("object_class",                  "Object class to track",                 list(OBJECT_CLASS_MAP)),
]


def run_configure(path="config.json"):
    raw = dict(_DEFAULTS)
    if os.path.exists(path):
        with open(path) as f:
            raw.update(json.load(f))

    print("\n=== ZED Object Tracker — Configuration ===")
    print("Press Enter to keep the current value.\n")

    for key, desc, valid in _CONFIGURE_FIELDS:
        current = raw[key]
        display = str(current).lower() if isinstance(current, bool) else str(current)

        print(f"{key}  ({desc})")
        if valid is not None:
            print(f"  Options : {', '.join(valid)}")
        else:
            print(f"  Range   : 0-100")
        print(f"  Current : {display}")

        while True:
            val = input("  > ").strip()
            if val == "":
                break
            if valid is not None:
                if val not in valid:
                    print(f"  Invalid. Choose from: {', '.join(valid)}")
                    continue
            else:
                try:
                    v = int(val)
                    if not (0 <= v <= 100):
                        raise ValueError
                except ValueError:
                    print("  Invalid. Enter an integer between 0 and 100.")
                    continue
            raw[key] = val
            break
        print()

    raw["sdk_verbose"] = int(raw["sdk_verbose"])
    raw["enable_tracking"] = str(raw["enable_tracking"]).lower() == "true"
    raw["enable_segmentation"] = str(raw["enable_segmentation"]).lower() == "true"
    raw["detection_confidence_threshold"] = int(raw["detection_confidence_threshold"])

    with open(path, "w") as f:
        json.dump(raw, f, indent=4)
    print(f"Saved to {path}.\n")


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
