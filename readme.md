# Intelligent Machines – Leader Arm Digital Twin

A documented digital twin project for reading a physical **leader arm** with potentiometers, calibrating its joints, and streaming the resulting joint angles to a digital robot model.

This repository contains the **full project version**, including both the original **Blender-based workflow** and the newer **web-based workflow**. It was developed from the original *Intelligent Machines* course assignment, which focuses on controlling a digital twin in real time from potentiometer input and explicitly references Blender scripting as part of that workflow.

For a smaller and easier-to-follow version that focuses only on the core concepts, see the **Minimum Working Example (MWE)**:  
[**Kinderuniversiteit_LeaderArm-DigitalTwin_MWE**](https://github.com/tobethieren/Kinderuniversiteit_LeaderArm-DigitalTwin_MWE)

---

## Repository overview

```text
.
├── blender/                  # Blender-side assets and Blender listener script
│   ├── blender_udp_listener.py
│   └── scene/
├── docs/                     # Project documentation
├── host/                     # PC-side launchers and stream bridges
│   ├── blender/              # Serial -> UDP -> Blender workflow
│   └── web/                  # Serial -> WebSocket -> browser workflow
├── lib/leader_arm/           # Shared embedded library code
├── reference/                # External reference material and attribution
├── src/apps/                 # PlatformIO application entry points
└── web/                      # Browser-based digital twin viewer
```

---

## Supported workflows

### 1. Web workflow

This is the preferred workflow for most users.

**Data path:**

```text
Leader arm hardware
-> Arduino / Nano Every
-> serial CSV stream
-> host/web/serial_to_websocket.py
-> WebSocket
-> web/ Three.js viewer
```

Why this workflow exists:

- easier to demo,
- easier to share,
- easier to host,
- no Blender session required during use.

### 2. Blender workflow

This is the original workflow and remains fully supported.

**Data path:**

```text
Leader arm hardware
-> Arduino / Nano Every
-> serial CSV stream
-> host/blender/serial_to_udp_brigde.py
-> UDP
-> blender/blender_udp_listener.py
-> Blender armature
```

Why this workflow still exists:

- it matches the original assignment direction,
- it is useful while rigging or validating the digital twin,
- it preserves the original desktop workflow.

---

## Quick start

### Embedded side

1. Connect the leader arm potentiometers to the pins defined in `lib/leader_arm/include/LeaderArmConfig.h`.
2. Upload the calibration firmware:
   - `pio run -e calibration -t upload`
3. Run the interactive calibration over serial.
4. Upload the streaming firmware:
   - `pio run -e stream_to_pc -t upload`

### Web side

1. Open `host/web/config.json` and verify the serial port and WebSocket settings.
2. Install the web dependencies once:
   - `cd web`
   - `npm install`
3. Start the launcher:
   - `python host/web/launcher.py`
4. Open the browser viewer, usually at `http://127.0.0.1:5173`.

### Blender side

1. Open the Blender scene from `blender/scene/`.
2. Run `blender/blender_udp_listener.py` inside Blender.
3. Start the Blender launcher:
   - `python host/blender/launcher.py`

More detailed instructions are available in:

- [`docs/setup.md`](docs/setup.md)
- [`docs/calibration.md`](docs/calibration.md)
- [`docs/architecture.md`](docs/architecture.md)

---

## Important folders

### `blender/`
Contains the Blender listener script and the `.blend` scene files.

- The **web** scene is the source scene used to export the GLB file for the browser version.
- The **non-web** Blender scene remains in the repository for the classic Blender workflow.

See [`blender/README.md`](blender/README.md) and [`blender/scene/README.md`](blender/scene/README.md).

### `host/`
Contains the two host-side workflows:

- `host/blender/` for the Blender route,
- `host/web/` for the web route.

Both are kept because the project started with Blender first and later expanded with a browser-based workflow to simplify usage and public sharing.

### `lib/leader_arm/`
Shared embedded code for:

- pin configuration,
- calibration defaults,
- analog filtering,
- EEPROM-backed settings,
- raw-to-angle conversion.

### `reference/`
Contains attribution, licensing context, creator references, and supporting material related to the original external model source.

---

## Full project vs. MWE

This repository is the **complete project version**. It includes the broader repository structure, both supported host workflows, the Blender pipeline, the web viewer pipeline, and the full supporting documentation around the project.

If you are only looking for the **core setup** needed to understand the main idea, use the **Minimum Working Example (MWE)** instead:  
[**Kinderuniversiteit_LeaderArm-DigitalTwin_MWE**](https://github.com/tobethieren/Kinderuniversiteit_LeaderArm-DigitalTwin_MWE)

The MWE is intended as the smaller, easier-to-read version of this project.

---

## Attribution and origin

The original creator of the **3D model** is **Build Some Stuff**.

- YouTube channel: https://www.youtube.com/@buildsomestuff
- Printables model: *Compact Robot Arm Arduino 3D Printed*
- The original model page states that the design is the creator’s own work and is licensed under **CC BY-NC-ND 4.0**.

This repository also includes reference material in `reference/` to document the origin of the robot-control inspiration and the broader development context.

More details are documented in [`reference/README.md`](reference/README.md).

---

## Licensing

- **Code**: MIT (see [`LICENSE`](LICENSE)).
- **3D model assets and derived exports**: CC BY-NC-ND 4.0, with explicit academic-use permission from the original creator for this repository (see [`LICENSE-MODEL.md`](LICENSE-MODEL.md)).

### Cascading credit

License for this model: CC BY-NC-ND 4.0

Credits:

- Derivative work by: Tobe Thieren (2026)
- Based on the original work by: Build Some Stuff
- Source of the original: https://www.youtube.com/@buildsomestuff

This model was created for non-commercial, research-oriented use, with respect for the original creator and license.

### Public repository note

The upstream 3D model is licensed under **CC BY-NC-ND 4.0**, including the **ND** (*NoDerivatives*) restriction.

The original creator (**Build Some Stuff / Kelton Serra**) granted **explicit permission** for this repository to share its derived `.blend` and `.glb` assets for **academic purposes**, under the conditions described in the permission record.

If you want to create or distribute further derivatives, or use the model outside the intended academic and non-commercial context, you must contact the original creator directly: `buildsomestuff.business@gmail.com`.

See:

- [`LICENSE-MODEL.md`](LICENSE-MODEL.md)
- [`reference/permission-buildsomestuff.md`](reference/permission-buildsomestuff.md)

---

## Documentation map

- [`docs/setup.md`](docs/setup.md) – installation and run instructions
- [`docs/calibration.md`](docs/calibration.md) – calibration workflow and EEPROM behavior
- [`docs/architecture.md`](docs/architecture.md) – system architecture and data flow
