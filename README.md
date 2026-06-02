# zed-object-tracker

> **Work in progress.** This project is under active development.

Real-time object detection and tracking using a ZED stereo camera. Detects objects in 3D space and overlays bounding boxes with position data (X/Y/Z in meters) on the live camera feed.

## Features

- Live object detection using the ZED SDK
- 3D position output per detected object (X=right/left, Y=up/down, Z=distance in meters)
- Stable per-session object numbering with multi-digit keyboard selection
- Auto-select mode: continuously highlights the closest object by depth
- Visual overlay: bounding boxes, number badges, confidence percentages, position labels, crosshair
- Camera center crosshair marking the X=0, Y=0 origin point
- HUD: live FPS counter, object count, auto-select indicator, top-down position map (bottom-left corner)
- Overlay toggle: hide all text labels while keeping bounding boxes visible
- Throttled terminal output (once per second) for position logging

## Requirements

- [ZED SDK](https://www.stereolabs.com/developers/release/) with Python bindings (`pyzed`)
- ZED stereo camera
- Python 3.10+
- OpenCV (`cv2`)
- NumPy

## Usage

```bash
python main.py
```

The camera initialises, loads the object detection module, and begins processing frames. All based on the configurations saved in config.json. See config_example.json.

| Key | Action |
|-----|--------|
| `0`–`9` | Type a display number to select an object |
| `Enter` | Confirm selection (highlights object red) |
| `Backspace` | Delete last typed digit |
| `Esc` | Cancel input without changing selection |
| `c` | Toggle auto-select mode (always selects closest object) |
| `h` | Toggle overlay visibility (hides text labels, keeps bounding boxes) |
| `r` | Reset all object numbering and clear selection |
| `q` | Quit |

Detected objects are filtered to the configured class. All tunable parameters are set in `config.json` — see [Configuration](#configuration) below.

## Configuration

All parameters are set in `config.json`. Valid values are also listed as comments in `config.py`.

To edit the configuration interactively before starting the tracker, run:

```bash
python main.py --configure
```

This steps through each parameter, shows the current value and valid options, and saves the result to `config.json`. Press Enter to keep the current value for any parameter.

| Key | Valid values | Description |
|-----|--------------|-------------|
| `object_class` | `PERSON` `VEHICLE` `BAG` `ANIMAL` `ELECTRONICS` `FRUIT_VEGETABLE` `SPORT` | Object class to track. `FRUIT_VEGETABLE` covers fruit, vegetables, and similar round objects. |
| `detection_model` | `MULTI_CLASS_BOX_FAST` `MULTI_CLASS_BOX_MEDIUM` `MULTI_CLASS_BOX_ACCURATE` | Detection model. FAST = highest FPS, ACCURATE = best quality. |
| `depth_mode` | `PERFORMANCE` `QUALITY` `ULTRA` `NEURAL` `NEURAL_PLUS` | Depth estimation algorithm. Higher quality costs more compute. |
| `detection_confidence_threshold` | `0`–`100` | Minimum confidence to report a detection. Lower catches more objects but increases false positives. |
| `coordinate_units` | `MILLIMETER` `CENTIMETER` `METER` `INCH` `FOOT` | Unit for all X/Y/Z position values. |
| `enable_tracking` | `true` `false` | Keeps object IDs stable across frames. Disable to reduce CPU load. |
| `enable_segmentation` | `true` `false` | Per-object pixel masks. Disable to reduce CPU load. |
| `proximity_warning_threshold` | positive number | Distance threshold (in `coordinate_units`) reserved for future proximity features. |
| `sdk_verbose` | `0` `1` | ZED SDK log output. `0` = silent, `1` = verbose. |

## Hardware

Runs on a Jetson (ARM). Per-frame allocations and rendering calls are treated as expensive.

## License

See [LICENSE](LICENSE).
