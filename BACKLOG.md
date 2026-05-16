# Backlog

Ideas from the visualization phase brainstorm. Pick any item and ask Claude to implement it.

`[QUICK WIN]` = low effort, high value  
`[PERF RISK]` = flag and discuss before implementing on Jetson

---

## New Features

- **FPS counter overlay** [QUICK WIN] — rolling average over ~30 frames, rendered as a corner label; immediate visibility into rendering cost
- **Confidence visualization** [QUICK WIN] — show `TargetPosition.confidence` (captured but never displayed) as a percentage in the number badge, e.g. `#1 87%`
- **Deselect key** [QUICK WIN] — press `0` or Esc to set `selected_num = None`; currently no way to clear a selection
- **Coordinate axis legend** [QUICK WIN] — static corner text block (`X: →right  Y: ↑up  Z: ↗away`) drawn before the object loop; zero per-frame cost
- **Crosshair at camera center** — two thin lines at `(frame_w/2, frame_h/2)` showing where `X=0, Y=0` falls; one `cv2.line` call per frame
- **Distance-based box color coding** — map Z to a 3-way ramp (e.g. red < 1 m, yellow 1–2 m, green > 2 m) via simple `if/elif`; selected object keeps red with thicker border
- **"Closest object" auto-highlight mode** — toggle with `c`; auto-selects the object with smallest `z` each frame; one `min()` call
- **Reset numbering key** — press `r` to clear `id_to_num` and reset `next_num = 1`; useful between test runs without restarting
- **Overlay toggle** — press `h` to hide position label text while keeping bounding boxes; single boolean flag passed to `draw()`
- **Trajectory trails** [PERF RISK] — capped `deque` of past centroids per `track_id`, drawn as `cv2.polylines`; needs same pruning fix as `id_to_num`
- **Velocity estimation** — buffer last 2–5 positions per `track_id`, compute `Δx/Δt, Δy/Δt, Δz/Δt` in m/s; groundwork for robotic arm lead compensation
- **Position export / session logging** [PERF RISK] — toggle `l` to write JSON lines to a file; must buffer writes (background thread or non-empty-only) to avoid blocking the loop

---

## Optimizations

- **`id_to_num` grows without bound** (`main.py:78`) — add a `last_seen: dict[int, float]` and prune entries absent for ~1 s; use a grace period to tolerate brief ZED tracker dropout
- **`cv2.getTextSize` recomputed every frame** (`main.py:100`) [QUICK WIN] — hint label string never changes; compute `(w, h)` once before `while True:` and cache it
- **`frame.copy()` with zero targets** (`visualizer.py:16`) — full-frame copy happens even when `all_targets` is empty and only one text label is drawn; low impact but noted

---

## Readability / Comments

- **Magic font scales** (`visualizer.py:32,36`) — `0.6` and `0.45` could be named constants alongside `GREEN`, `RED`, `FONT`
- **Truncated comment** (`zed_detector.py:53`) — inline comment ends mid-sentence ("…for other classes or"); complete or trim
- **`bounding_box_2d` corner ordering** (`zed_detector.py:57–61`) — ZED returns (TL, TR, BR, BL); add one-line comment that indices 0 and 2 give the diagonal
- **ZED coordinate system at unpack site** (`zed_detector.py:55`) — note X=right, Y=up, Z=away at the point `obj.position` is unpacked; helps future arm-integration work

---

## UX / Interaction

- **Confidence in terminal output** [QUICK WIN] — `format_terminal_output` never prints `confidence`; add `conf: 87%` to each line
- **Window title** — `"ZED Tennis Ball Tracker"` hardcodes the object class; `"ZED Object Tracker"` is more neutral and survives class-filter changes

---

## Robotic Arm Readiness

- **Output interface** — UDP socket in a thin `publisher.py` emitting one JSON line per frame for the selected (or all) objects; settle early: does the arm pick its own target or receive only the selected one?
- **Timestamp in `TargetPosition`** — add `timestamp: float = 0.0` (monotonic, set at detection time); enables downstream velocity and staleness checks without touching the detector later
- **Velocity fields in `TargetPosition`** — add `vx/vy/vz: float = 0.0`; zero-cost now, no API break when velocity estimation lands
- **Coordinate frame transform hook** — add `# TODO: apply camera→world transform` comment at `zed_detector.py:55`; marks the seam before the arm mount pose is known
- **`get_selected_target()` helper** — extract `(all_targets, id_to_num, selected_num) -> TargetPosition | None` from `main.py`; clean seam for arm-control code to consume without replicating the `id_to_num` lookup
