# CLAUDE.md — ZED Object Tracker

## Project purpose
Real-time object tracking using a ZED stereo camera. The longer-term goal is to feed
detected object positions (x/y/z in meters) to a robotic arm.

## Hardware
- Runs on a **Jetson** (ARM CPU, limited compute). Treat every per-frame operation as
  potentially expensive.

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

### Key data type
`TargetPosition` (detector/zed_detector.py) — one detected object per frame:
- `x, y, z` — position in the configured coordinate unit (default: meters)
- `confidence` — 0.0–1.0
- `bbox` — (x1, y1, x2, y2) pixels
- `track_id` — stable ID from the ZED SDK tracker (persists across frames)

## Known gotchas
- At low confidence thresholds (< ~30), the multi-class model misclassifies people as
  FRUIT_VEGETABLE. Raise the threshold rather than adding a size filter.
- `cv2.LINE_AA` on text inside the object loop caused a significant FPS drop on Jetson.
- Printing multiple lines to stdout every frame blocks the loop noticeably on Jetson.
- The ZED SDK emits NaN coordinates for objects being tracked but not yet localized.
  These are filtered out in `zed_detector.py` before reaching the rest of the pipeline.
