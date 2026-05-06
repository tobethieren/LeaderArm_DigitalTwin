# Blender scenes

This folder contains the Blender scene files used in the project.

## Files

### `robot-arm_digital-twin-WEB.blend`
This is the **scene used for the web pipeline**.

It is the Blender scene that is used to prepare the digital twin for export to the **GLB file** that is then loaded by the browser-based version in `web/`.

In practice, this means:

- the scene is used to prepare pivots and export structure for the web viewer,
- the exported result is the GLB model used by the Three.js application,
- changes that affect the web model should normally start from this scene.

### `robot-arm_digital-twin.blend`
This is the **non-web Blender version**.

It stays in the repository on purpose and is used when choosing the **regular Blender route** found elsewhere in the codebase:

- `host/blender/launcher.py`
- `host/blender/serial_to_udp_brigde.py`
- `blender/blender_udp_listener.py`

This version is useful for the classic Blender workflow and for work that stays inside Blender rather than being exported to the web viewer.

## Notes

- `.blend1` and `.blend2` files are Blender backup files and should not be committed (they are ignored via the repository `.gitignore`).

## Licensing and attribution

The Blender scenes in this folder are part of the 3D model asset chain.

- Code license (repository code): MIT (see [`../../LICENSE`](../../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 (see [`../../LICENSE-MODEL.md`](../../LICENSE-MODEL.md))

### Cascading credit (waterfall attribution)

License for this model: CC BY-NC-ND 4.0

Credits:

Derivative work by: Tobe Thieren (2026)

Based on the original work by: Build Some Stuff

Source of the original: https://www.youtube.com/@buildsomestuff

This model was created for non-commercial, research purposes, with respect for the original license.

### Public repository warning (NoDerivatives)

The upstream 3D model is licensed under **CC BY-NC-ND 4.0** (the **ND** = *NoDerivatives* restriction).

The original creator (**Build Some Stuff / Kelton Serra**) has granted **explicit permission** for this repository to share its **derived** `.blend` and `.glb` assets for **academic purposes**, under the conditions described in the request.

If you want to create and/or distribute further derivatives (or use the model outside the intended academic/non-commercial context), you must contact the original creator directly: `buildsomestuff.business@gmail.com`.

See [`../../LICENSE-MODEL.md`](../../LICENSE-MODEL.md) and [`../../reference/permission-buildsomestuff.md`](../../reference/permission-buildsomestuff.md).
