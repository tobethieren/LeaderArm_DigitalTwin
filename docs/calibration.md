# Calibration

Calibration translates raw potentiometer readings into meaningful joint angles.

Without calibration, the digital twin may move in the wrong direction, use the wrong range, or stop short of the real arm's motion.

## Why calibration is necessary

The assignment requires reading potentiometer values from the leader arm and mapping them to the digital twin so that the model moves correctly according to the input values. Calibration is the step that makes that mapping usable.

## Where calibration is implemented

Main file:

- `src/apps/calibration.cpp`

Shared support:

- `lib/leader_arm/include/LeaderArmTypes.h`
- `lib/leader_arm/include/LeaderArmSettings.h`
- `lib/leader_arm/src/LeaderArmSettings.cpp`

## How the interactive calibration works

For each axis, the calibration app asks for two physical limit positions.

Example pattern:

1. move the joint to the first limit,
2. press Enter,
3. record the raw analog value,
4. move the joint to the second limit,
5. press Enter,
6. record the second raw analog value,
7. store both the raw range and the corresponding angle range.

The code then ensures that `rawMin < rawMax`, while preserving the correct matching between raw values and physical angles.

## Stored values

Each joint stores:

- `rawMin`
- `rawMax`
- `angleMinDeg`
- `angleMaxDeg`

These values are saved in EEPROM so calibration does not need to be repeated every time the board restarts.

## EEPROM behavior

`stream_to_pc.cpp` attempts to load saved settings from EEPROM at startup.

Possible outcomes:

- valid calibration found -> use saved calibration,
- invalid or missing calibration -> use fallback/default values.

The launcher scripts check this state and can offer to run calibration when needed.

## Calibrated joints in the current implementation

The current implementation works with four joints:

- basis
- main arm
- fore arm
- wrist

## Practical calibration workflow

### From PlatformIO directly

```bash
pio run -e calibration -t upload
```

Then open the serial monitor at `115200` baud and follow the prompts.

### From the host launcher

Run one of:

```bash
python host/web/launcher.py
```

or

```bash
python host/blender/launcher.py
```

The launcher can:

- upload the streaming firmware,
- inspect the EEPROM state,
- ask whether calibration should be run,
- upload the calibration firmware when needed,
- switch back to the streaming firmware after calibration.

## Tuning notes

You will probably need to adjust the requested calibration angles in `src/apps/calibration.cpp` to match your physical build.

Typical reasons:

- potentiometer mounting differs,
- joint directions are inverted,
- your mechanical limits are different from the defaults,
- your digital twin uses a different zero position.

## Licensing and attribution

- Code license (repository code): MIT (see [`../LICENSE`](../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../LICENSE-MODEL.md`](../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../reference/permission-buildsomestuff.md`](../reference/permission-buildsomestuff.md)
