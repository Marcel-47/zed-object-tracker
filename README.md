# zed-object-tracker

Real-time object detection and tracking using a ZED stereo camera. Detects objects in 3D space and overlays bounding boxes with position data (X/Y/Z in meters) on the live camera feed.

## Features

- Live object detection using the ZED SDK's configured model
- 3D position output (left/right, up/down, distance) per detected object
- Filters for sport-class objects (e.g. balls)
- Visual overlay with bounding boxes and labeled coordinates via OpenCV

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

The camera will initialise, load the object detection module, and begin processing frames. Detected objects of the configured class are highlighted with a bounding box and their 3D position relative to the camera.


## License

See [LICENSE](LICENSE).
