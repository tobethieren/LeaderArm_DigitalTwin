# Architecture

This project is split into four layers:

1. **embedded firmware** on the microcontroller,
2. **host bridge scripts** on the PC,
3. **visualization** in Blender or the browser,
4. **assets and reference material** for the digital twin model.

The course assignment describes the core idea clearly: read potentiometer values on a microcontroller and translate them to movement in the digital twin model in real time.

## High-level system view

### Embedded layer

Files:

- `platformio.ini`
- `src/apps/calibration.cpp`
- `src/apps/stream_to_pc.cpp`
- `lib/leader_arm/`

Responsibilities:

- read analog joint inputs,
- calibrate each axis,
- persist calibration in EEPROM,
- convert raw values to degrees,
- stream joint angles over serial.

### Host layer

Files:

- `host/blender/*`
- `host/web/*`

Responsibilities:

- detect the serial device,
- optionally upload firmware,
- optionally run calibration,
- bridge serial data to the chosen visualization route.

### Visualization layer

Two supported front ends exist.

#### Blender front end

Files:

- `blender/blender_udp_listener.py`
- `blender/scene/*.blend`

Responsibilities:

- receive UDP packets,
- map angles to armature bones,
- update the Blender scene pose.

#### Web front end

Files:

- `web/src/main.js`
- `web/public/models/robot-arm_digital-twin.glb`

Responsibilities:

- connect to the local WebSocket server,
- receive the latest pose,
- map joint values to named pivot nodes,
- render the robot with Three.js.

**Public distribution notice (NoDerivatives):** The upstream 3D model is licensed under **CC BY-NC-ND 4.0** (the **ND** = *NoDerivatives* restriction). The original creator (**Build Some Stuff / Kelton Serra**) has granted **explicit permission** for this repository to share its **derived** model assets for **academic purposes**, under the conditions described in the request. If you want to create and/or distribute further derivatives (or use the model outside the intended academic/non-commercial context), contact the original creator directly: `buildsomestuff.business@gmail.com`. See [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md) and [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md).

## Data flow

### Web route

```text
Potentiometers
-> analogRead()
-> calibrated joint angles
-> serial CSV
-> serial_to_websocket.py
-> JSON over WebSocket
-> web/src/main.js
-> pivot node rotations in Three.js
```

### Blender route

```text
Potentiometers
-> analogRead()
-> calibrated joint angles
-> serial CSV
-> serial_to_udp_brigde.py
-> UDP CSV payload
-> blender_udp_listener.py
-> Blender pose bone rotations
```

## Calibration architecture

The firmware is intentionally split into two modes.

### Calibration mode

`src/apps/calibration.cpp` is used only when collecting and storing calibration values.

### Streaming mode

`src/apps/stream_to_pc.cpp` is used during normal operation.

This separation keeps runtime streaming simple while still allowing guided setup when the hardware changes.

## Why both Blender and web exist

The project originally followed the Blender-focused route suggested by the assignment. Later, the web viewer was added because it is easier to host, easier to demo, and easier to share publicly.

That is why:

- `host/blender/` still exists,
- `host/web/` was added later,
- the non-web Blender files are intentionally still kept.

## Licensing and attribution

- Code license (repository code): MIT (see [`../LICENSE`](../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md)
