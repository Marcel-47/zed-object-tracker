# zed-object-tracker

> **Work in progress.** This project is under active development.

Real-time object detection and tracking using a ZED stereo camera. Detects objects in 3D space and overlays bounding boxes with position data (X/Y/Z in meters) on the live camera feed. Intended as the perception layer for a robotic arm controller.

## Features

- Live object detection using the ZED SDK
- 3D position output per detected object (X=right/left, Y=up/down, Z=distance in meters)
- Stable per-session object numbering with manual selection (digit keys)
- Visual overlay: bounding boxes, number badges, position labels
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

Detected objects are filtered to the configured class. Confidence threshold and object class can be changed in `main.py` and `detector/zed_detector.py`.

## Architecture

```
main.py                  — camera init, main loop, keypress handling, terminal output
detector/zed_detector.py — ZED SDK wrapper, returns list[TargetPosition]
visualizer/visualizer.py — draws boxes, number badges, and position labels onto frames
```

## Hardware

Runs on a Jetson (ARM). Per-frame allocations and rendering calls are treated as expensive.

## Backlog

Planned improvements are tracked in [BACKLOG.md](BACKLOG.md).

## License

See [LICENSE](LICENSE).
