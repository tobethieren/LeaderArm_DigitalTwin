# Firmware applications

This folder contains the two main firmware entry points used by the project.

## `calibration.cpp`

Interactive calibration firmware.

Purpose:

- guides the user through the joint limits one axis at a time,
- records raw analog readings at two known physical positions,
- converts those measurements into calibration ranges,
- stores the result in EEPROM.

Practical flow:

1. flash the calibration environment,
2. open the serial monitor,
3. follow the prompts,
4. move each joint to the requested limit positions,
5. press Enter when asked,
6. save the resulting calibration.

This is the firmware that turns a rough analog setup into a meaningful angle mapping.

## `stream_to_pc.cpp`

Runtime streaming firmware.

Purpose:

- load the saved calibration from EEPROM,
- fall back to defaults when needed,
- read all configured analog inputs repeatedly,
- convert the raw readings to degrees,
- emit a four-value CSV line over serial.

The output is meant for the host-side bridge scripts in `host/blender/` and `host/web/`.

## Relationship with `platformio.ini`

`platformio.ini` defines two build environments:

- `calibration`
- `stream_to_pc`

Each environment uses only the matching application file from this folder.

## Licensing and attribution

- Code license (repository code): MIT (see [`../../LICENSE`](../../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../../LICENSE-MODEL.md`](../../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../../reference/permission-buildsomestuff.md`](../../reference/permission-buildsomestuff.md)
