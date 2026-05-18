# zed-object-tracker

> **Work in progress.** This project is under active development.

Real-time object detection and tracking using a ZED stereo camera. Detects objects in 3D space and overlays bounding boxes with position data (X/Y/Z in meters) on the live camera feed. Intended as the perception layer for a robotic arm controller.

## Features

- Live object detection using the ZED SDK
- 3D position output per detected object (X=right/left, Y=up/down, Z=distance in meters)
- Stable per-session object numbering with manual selection (digit keys)
- Visual overlay: bounding boxes, number badges, position labels, crosshair, confidence bar
- Proximity warning: box turns orange and shows CLOSE label when object is within threshold distance
- HUD: live FPS counter, object count, top-down position map (bottom-left corner)
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

The camera initialises, loads the object detection module, and begins processing frames.

| Key | Action |
|-----|--------|
| `1`–`9` | Select object by display number (highlights red) |
| `0` | Deselect |
| `q` | Quit |

Detected objects are filtered to the configured class. All tunable parameters are set in `config.json` — see [Configuration](#configuration) below.

## Configuration

All parameters are set in `config.json`. Valid values are also listed as comments in `config.py`.

To edit the configuration interactively before starting the tracker, run:

```bash
python main.py --configure
```

This steps through each parameter, shows the current value and valid options, and saves the result to `config.json`. Press Enter to keep the current value for any parameter.

| Key | Default | Valid values | Description |
|-----|---------|--------------|-------------|
| `depth_mode` | `NEURAL` | `PERFORMANCE` `QUALITY` `ULTRA` `NEURAL` `NEURAL_PLUS` | Depth estimation algorithm. Higher quality costs more compute. |
| `coordinate_units` | `METER` | `MILLIMETER` `CENTIMETER` `METER` `INCH` `FOOT` | Unit for all X/Y/Z position values. |
| `sdk_verbose` | `1` | `0` `1` | ZED SDK log output. `0` = silent, `1` = verbose. |
| `enable_tracking` | `true` | `true` `false` | Keeps object IDs stable across frames. Disable to reduce CPU load. |
| `enable_segmentation` | `false` | `true` `false` | Per-object pixel masks. Disable to reduce CPU load. |
| `detection_model` | `MULTI_CLASS_BOX_ACCURATE` | `MULTI_CLASS_BOX_FAST` `MULTI_CLASS_BOX_MEDIUM` `MULTI_CLASS_BOX_ACCURATE` | Detection model. FAST = highest FPS, ACCURATE = best quality. |
| `detection_confidence_threshold` | `40` | `0`–`100` | Minimum confidence to report a detection. Lower catches more objects but increases false positives. |
| `object_class` | `FRUIT_VEGETABLE` | `PERSON` `VEHICLE` `BAG` `ANIMAL` `ELECTRONICS` `FRUIT_VEGETABLE` `SPORT` | Object class to track. `FRUIT_VEGETABLE` covers fruit, vegetables, and similar round objects. |
| `proximity_warning_threshold` | `1.0` | positive number | Distance (in `coordinate_units`) below which a box turns orange and shows a CLOSE label. |

## Architecture

```
main.py                  — camera init, main loop, FPS tracking, keypress handling, terminal output
config.py                — config loading, enum mappings, interactive --configure prompt
config.json              — user-editable parameters
detector/zed_detector.py — ZED SDK wrapper, returns list[TargetPosition]
visualizer/visualizer.py — draws per-object overlays, HUD (FPS, count, map), proximity warnings
```

## Hardware

Runs on a Jetson (ARM). Per-frame allocations and rendering calls are treated as expensive.

## License

See [LICENSE](LICENSE).
