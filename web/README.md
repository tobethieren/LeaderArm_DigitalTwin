# Web digital twin viewer

This folder contains the browser-based version of the digital twin.

It is intended to be the simpler and more shareable alternative to the original Blender route.

## What it does

The web app:

- loads the exported GLB robot model,
- connects to the local WebSocket server,
- receives live joint angles,
- applies those angles to pivot nodes in the scene,
- renders the robot in real time with Three.js.

## Main files

- `src/main.js` – application logic, scene setup, model loading, live pose updates
- `src/style.css` – styling for the viewer UI
- `index.html` – application shell and UI structure
- `public/models/robot-arm_digital-twin.glb` – web-ready model asset
- `package.json` – npm scripts and dependencies

## Public repository warning (NoDerivatives)

The upstream 3D model is licensed under **CC BY-NC-ND 4.0** (the **ND** = *NoDerivatives* restriction).

The original creator (**Build Some Stuff / Kelton Serra**) has granted **explicit permission** for this repository to share its **derived** `.blend` and `.glb` assets for **academic purposes**, under the conditions described in the request.

If you want to create and/or distribute further derivatives (or use the model outside the intended academic/non-commercial context), you must contact the original creator directly: `buildsomestuff.business@gmail.com`.

See [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md) and [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md).

## Runtime architecture

```text
serial_to_websocket.py
-> WebSocket server
-> browser client in src/main.js
-> Three.js scene
-> pivot node rotations
```

## Important implementation detail

The browser viewer expects named pivot nodes in the GLB model:

- `rotating_base_pivot`
- `main_arm_pivot`
- `fore_arm_pivot`
- `wrist_pivot`

Those names must exist in the exported GLB. If they change in Blender, update the `JOINTS` mapping in `src/main.js`.

## Running locally

```bash
cd web
npm install
npm run dev
```

The host-side launcher in `host/web/launcher.py` can also start the dev server automatically.

## Licensing and attribution

- Code license (repository code): MIT (see [`../LICENSE`](../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md))
