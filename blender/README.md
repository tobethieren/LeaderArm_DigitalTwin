# Blender workflow

This folder contains everything related to the **classic Blender-based digital twin workflow**.

## Contents

- `blender_udp_listener.py` – Blender-side listener that receives UDP packets and applies the joint angles to the armature bones.
- `scene/` – Blender scene files used during rigging, validation, export, and the original Blender route.

## How this workflow works

```text
Microcontroller
-> serial CSV
-> host/blender/serial_to_udp_brigde.py
-> UDP packets
-> blender_udp_listener.py
-> Blender armature pose bones
```

The listener expects four joint angles in CSV format:

```text
basis,main,fore,wrist
```

Example:

```text
12.50,-30.00,48.20,5.00
```

## `blender_udp_listener.py`

This script is meant to be run **inside Blender's Python environment**.

Responsibilities:

- opens a non-blocking UDP socket,
- listens on `127.0.0.1:5005` by default,
- parses four incoming angles,
- maps them to the configured bones,
- updates the armature pose in real time.

Configured bones:

- `BONE_BASIS`
- `BONE_MAIN_ARM`
- `BONE_FORE_ARM`
- `BONE_WRIST`

If your armature names or axes change, update the `BONES` mapping inside the script.

## When to use this route

Use the Blender route when you want to:

- work directly with the `.blend` digital twin,
- test rigging and armature behavior,
- validate bone axes and sign directions,
- stay close to the original assignment workflow.

For most demos and public sharing, the browser workflow in `web/` is usually easier.

## Licensing and attribution

- Code license (repository code): MIT (see [`../LICENSE`](../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md))

### Public repository warning (NoDerivatives)

The upstream 3D model is licensed under **CC BY-NC-ND 4.0** (the **ND** = *NoDerivatives* restriction).

The original creator (**Build Some Stuff / Kelton Serra**) has granted **explicit permission** for this repository to share its **derived** `.blend` and `.glb` assets for **academic purposes**, under the conditions described in the request.

If you want to create and/or distribute further derivatives (or use the model outside the intended academic/non-commercial context), you must contact the original creator directly: `buildsomestuff.business@gmail.com`.

See [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md) and [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md).
