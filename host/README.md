# Host-side tooling

This folder contains the **PC-side bridge scripts and launchers**.

## Why there are two subfolders

There are two host workflows:

- `host/blender/`
- `host/web/`

Both are kept because the project originally started with the **Blender workflow** and later switched to a **web workflow** to make usage and demos simpler.

The original Blender way still works and is intentionally preserved.

## Licensing and attribution

- Code license (repository code): MIT (see [`../LICENSE`](../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md)

## Folder summary

### `host/blender/`
Used when you want to work with the Blender digital twin.

- uploads firmware if needed,
- checks calibration state,
- optionally runs calibration,
- reads serial data from the microcontroller,
- forwards it over UDP to Blender.

### `host/web/`
Used when you want to work with the web digital twin.

- uploads firmware if needed,
- checks calibration state,
- optionally runs calibration,
- reads serial data from the microcontroller,
- forwards it over WebSocket to the browser,
- can optionally auto-start the website.
