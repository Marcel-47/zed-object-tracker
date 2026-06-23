import json
import os
import pyzed.sl as sl


# Valid values for "object_class" in config.json.
# FRUIT_VEGETABLE covers fruit, vegetables, and similar round objects.
OBJECT_CLASS_MAP = {
    "PERSON":          sl.OBJECT_CLASS.PERSON,
    "VEHICLE":         sl.OBJECT_CLASS.VEHICLE,
    "BAG":             sl.OBJECT_CLASS.BAG,
    "ANIMAL":          sl.OBJECT_CLASS.ANIMAL,
    "ELECTRONICS":     sl.OBJECT_CLASS.ELECTRONICS,
    "FRUIT_VEGETABLE": sl.OBJECT_CLASS.FRUIT_VEGETABLE,  # default
    "SPORT":           sl.OBJECT_CLASS.SPORT,
}

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

# Short label printed after each X/Y/Z value in the terminal and the UI.
UNIT_LABEL_MAP = {
    "MILLIMETER": "mm",
    "CENTIMETER": "cm",
    "METER":      "m",
    "INCH":       "in",
    "FOOT":       "ft",
}

# How many of the configured unit make up one meter. The top-down map is sized
# in meters; this factor converts those meter ranges into the active unit so the
# map covers the same physical area regardless of coordinate_units.
UNIT_PER_METER = {
    "MILLIMETER": 1000.0,
    "CENTIMETER": 100.0,
    "METER":      1.0,
    "INCH":       39.3700787,
    "FOOT":       3.2808399,
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

# Valid values for "lighting" in config.json.
# Selects the HSV saturation/value floors the color filter uses.
# indoor:  lower floors for dimmer indoor light (default)
# outdoor: raised floors for brighter outdoor light
# Only affects the color filter; the detection model is unaffected.
LIGHTING_OPTIONS = ["indoor", "outdoor"]

_DEFAULTS = {
    "depth_mode":                    "NEURAL",           # see DEPTH_MODE_MAP for valid values
    "coordinate_units":              "METER",            # see UNIT_MAP for valid values
    "sdk_verbose":                   1,                  # 0 = silent, 1 = verbose SDK logging
    "enable_tracking":               True,               # keeps object IDs stable across frames
    "enable_segmentation":           False,              # per-object pixel masks; disable to reduce CPU load
    "detection_model":               "MULTI_CLASS_BOX_ACCURATE",  # see DETECTION_MODEL_MAP for valid values
    "detection_confidence_threshold": 40,                # 0–100; lower catches more objects but increases false positives
    "object_class":                  "FRUIT_VEGETABLE",  # see OBJECT_CLASS_MAP for valid values
    "lighting":                      "indoor",           # see LIGHTING_OPTIONS; tunes the color filter for indoor/outdoor light
}


# Drives the --configure prompt: (key, description, valid options or None for free numeric input)
_CONFIGURE_FIELDS = [
    ("object_class",
     "Object class to track. E.g., FRUIT_VEGETABLE covers fruit, vegetables, and similar round objects. See ZED SDK docs for details.",
     list(OBJECT_CLASS_MAP)),
    ("detection_model",
     "Balances detection quality against frame rate. FAST maximizes FPS; ACCURATE maximizes detection quality.",
     list(DETECTION_MODEL_MAP)),
    ("depth_mode",
     "Depth estimation algorithm. Higher modes are more accurate but cost more compute on the Jetson.",
     list(DEPTH_MODE_MAP)),
    ("detection_confidence_threshold",
     "Minimum confidence (0-100) to report a detection. E.g., below ~30, people may be misclassified as FRUIT_VEGETABLE.",
     None),
    ("lighting",
     "Lighting preset for the color filter. indoor uses lower HSV saturation/value floors; outdoor raises them for brighter light. Only affects the color filter.",
     LIGHTING_OPTIONS),
    ("coordinate_units",
     "Unit for all X/Y/Z position values reported per detected object.",
     list(UNIT_MAP)),
    ("enable_tracking",
     "Keeps object IDs stable across frames. Disabling reduces CPU load but IDs will reset each frame.",
     ["true", "false"]),
    ("enable_segmentation",
     "Generates a per-object pixel mask. Disable to reduce CPU load — not used by the visualizer.",
     ["true", "false"]),
    ("sdk_verbose",
     "ZED SDK log output to the terminal. Set to 0 to suppress SDK messages at startup.",
     ["0", "1"]),
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

        print(f"{key}")
        print(f"  {desc}")
        if valid is not None:
            print(f"  Options : {', '.join(valid)}")
        else:
            print(f"  Range   : 0-100 (integer)")
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
        "coordinate_unit_label":         UNIT_LABEL_MAP[cfg["coordinate_units"]],
        "coordinate_unit_per_meter":     UNIT_PER_METER[cfg["coordinate_units"]],
        "sdk_verbose":                   int(cfg["sdk_verbose"]),
        "enable_tracking":               bool(cfg["enable_tracking"]),
        "enable_segmentation":           bool(cfg["enable_segmentation"]),
        "detection_model":               DETECTION_MODEL_MAP[cfg["detection_model"]],
        "detection_confidence_threshold": int(cfg["detection_confidence_threshold"]),
        "object_class":                  OBJECT_CLASS_MAP[cfg["object_class"]],
        "lighting":                      str(cfg["lighting"]).lower(),
    }
