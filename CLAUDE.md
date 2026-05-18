# CLAUDE.md — ZED Object Tracker

## Project purpose
Real-time object tracking using a ZED stereo camera. The longer-term goal is to feed
detected object positions (x/y/z in meters) to a robotic arm.

**Current phase: visualization.** Detailed, informative visuals are a priority right
now. Invest in making the overlay clear and useful. When the project switches to robotic
arm integration, visual quality becomes secondary to position accuracy and output
latency — update this file at that point.

## Hardware
- Runs on a **Jetson** (ARM CPU, limited compute). Treat every per-frame operation as
  potentially expensive.
- Only the ZED SDK and OpenCV are available for camera input and rendering.

## Writing style
Applies to README files, code comments, commit messages, and any other written documentation — not to conversational responses.

- Avoid rhetorical contrast formulas ("This is not X, this is Y" / "Not X, but Y") used for dramatic effect.
- Avoid em dashes (–) as stylistic connectors between sentence parts. Restructure the sentence instead.

## How to approach changes
Always **explain the plan before touching code**. Describe what will change and why,
then implement. If the approach has a meaningful tradeoff, name it.

## What not to do without asking before
- Do not refactor or clean up code that is unrelated to the current task.
- Do not switch the detection model (`MULTI_CLASS_BOX_ACCURATE`) or change confidence
  thresholds — these are tuned to the environment.
- Do not add comments unless the reason behind the code is genuinely non-obvious.
- Do not remove existing comments without asking.
- Do not introduce new abstractions or helper functions beyond what the task requires.

## Performance rules (Jetson-specific)
During the current visualization phase, rendering quality takes priority — use
`LINE_AA`, richer overlays, etc. where it improves clarity. Still avoid gratuitous
waste:
- Do not call `print()` every frame; throttle terminal output (currently once per second).
- Keep per-frame allocations minimal (avoid unnecessary `.copy()`, large intermediate arrays).
- If a rendering choice causes a noticeable FPS drop, flag it and discuss the tradeoff
  rather than silently stripping it out.

Note: `cv2.LINE_AA` inside per-object loops caused an FPS drop in a prior session —
worth monitoring if many objects are on screen simultaneously.

## Architecture overview
```
main.py                  — camera init, main loop, keypress handling, terminal output
config.py                — config loading, enum mappings, interactive --configure prompt
config.json              — user-editable parameters (edit directly or via --configure)
detector/zed_detector.py — wraps ZED SDK object detection, returns list[TargetPosition]
visualizer/visualizer.py — draws boxes, number badges, and position labels onto frames
```

### Key data type
`TargetPosition` (detector/zed_detector.py) — one detected object per frame:
- `x, y, z` — position in the configured coordinate unit (default: meters)
- `confidence` — 0.0–1.0
- `bbox` — (x1, y1, x2, y2) pixels
- `track_id` — stable ID from the ZED SDK tracker (persists across frames)

### Object numbering
`main.py` maintains `id_to_num: dict[int, int]` mapping ZED track IDs to stable
display numbers (1, 2, 3…). Numbers are never reused within a session.

### Selection
The user presses a digit key to select an object by its display number. Selected object
gets a red box; all others are green. No automatic selection logic.

### Configuration
All camera and detection parameters live in `config.json`. `config.py` loads the file,
applies defaults for missing keys, and resolves string names to `sl.*` enum values.
Run `python main.py --configure` to edit parameters interactively before starting.

Currently tracking `FRUIT_VEGETABLE` (tennis balls fall into this class). Default
confidence threshold is 40 — too low causes false positives (people misclassified),
too high misses distant balls.

Planned next CLI feature: `--set key=value` session overrides (e.g.
`--set detection_confidence_threshold=50`) that apply for one run without modifying
`config.json`.

## Known gotchas
- At low confidence thresholds (< ~30), the multi-class model misclassifies people as
  FRUIT_VEGETABLE. Raise the threshold rather than adding a size filter.
- `cv2.LINE_AA` on text inside the object loop caused a significant FPS drop on Jetson.
- Printing multiple lines to stdout every frame blocks the loop noticeably on Jetson.
