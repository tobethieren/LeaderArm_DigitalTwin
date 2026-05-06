# Setup

This document explains how to set up the project from scratch.

## 1. Requirements

### Hardware

- leader arm with potentiometers
- supported microcontroller, currently configured for **Arduino Nano Every** in `platformio.ini`
- USB cable to connect the board to the PC

### Software

- Python 3
- PlatformIO CLI
- Node.js and npm for the web viewer
- Blender for the Blender workflow

## 2. Repository structure to understand first

Before running anything, know the main routes:

- embedded firmware lives in `src/` and `lib/leader_arm/`
- Blender tools live in `blender/` and `host/blender/`
- web tools live in `web/` and `host/web/`
- project-level docs live in `docs/`

## 3. Embedded firmware setup

The project defines two PlatformIO environments:

- `calibration`
- `stream_to_pc`

### Upload the calibration firmware

```bash
pio run -e calibration -t upload
```

### Upload the streaming firmware

```bash
pio run -e stream_to_pc -t upload
```

## 4. Python dependencies

The host scripts use Python packages such as:

- `pyserial`
- `websockets`

Install them in your environment if needed:

```bash
pip install pyserial websockets
```

## 5. Web workflow setup

### Install web dependencies

```bash
cd web
npm install
```

### Start manually

In one terminal:

```bash
python host/web/serial_to_websocket.py
```

In another terminal:

```bash
cd web
npm run dev
```

### Or use the launcher

```bash
python host/web/launcher.py
```

The launcher can automate:

- serial-port selection,
- firmware upload,
- EEPROM check,
- optional calibration,
- optional website startup,
- WebSocket bridge startup.

## 6. Blender workflow setup

### Start manually

1. Open the desired Blender scene.

**Public distribution notice (NoDerivatives):** The upstream 3D model is licensed under **CC BY-NC-ND 4.0** (the **ND** = *NoDerivatives* restriction). The original creator (**Build Some Stuff / Kelton Serra**) has granted **explicit permission** for this repository to share its **derived** model assets for **academic purposes**, under the conditions described in the request. If you want to create and/or distribute further derivatives (or use the model outside the intended academic/non-commercial context), contact the original creator directly: `buildsomestuff.business@gmail.com`. See [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md) and [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md).

2. Run `blender/blender_udp_listener.py` in Blender.
3. In a terminal, run:

```bash
python host/blender/serial_to_udp_brigde.py
```

### Or use the launcher

```bash
python host/blender/launcher.py
```

The launcher can automate:

- serial-port selection,
- firmware upload,
- EEPROM check,
- optional calibration,
- UDP bridge startup.

## 7. Configuration files

Each host route contains:

- `config.example.json`
- `config.json`

Recommended public-project practice:

- keep `config.example.json` as the documented template,
- edit `config.json` locally for your own machine.

## 8. Web asset export reminder

The web viewer depends on the GLB asset located at:

- `web/public/models/robot-arm_digital-twin.glb`

That asset should be exported from:

- `blender/scene/robot-arm_digital-twin-WEB.blend`

**Public distribution notice (NoDerivatives):** The upstream 3D model is licensed under **CC BY-NC-ND 4.0** (the **ND** = *NoDerivatives* restriction). The original creator (**Build Some Stuff / Kelton Serra**) has granted **explicit permission** for this repository to share its **derived** model assets for **academic purposes**, under the conditions described in the request. If you want to create and/or distribute further derivatives (or use the model outside the intended academic/non-commercial context), contact the original creator directly: `buildsomestuff.business@gmail.com`. See [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md) and [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md).

## 9. Common issues

### Serial port busy

If the launcher says the serial port cannot be opened:

- close PlatformIO Serial Monitor,
- close Arduino IDE serial tools,
- close any other program that may still be attached to the board.

### Model loads but does not move

Check:

- the WebSocket server is running,
- the browser is connected,
- the pivot node names in the GLB match `web/src/main.js`,
- the calibration produced sensible angle ranges.

### Blender scene does not move

Check:

- the UDP bridge is running,
- Blender is listening on the same IP/port,
- the armature object is named `Armature`,
- the bone names match the mapping in `blender_udp_listener.py`.

## Licensing and attribution

- Code license (repository code): MIT (see [`../LICENSE`](../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md)
