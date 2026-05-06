# `lib/leader_arm`

Shared library code for the leader arm firmware.

## Structure

- `include/` – public headers and shared data structures
- `src/` – implementations for analog reading and EEPROM-backed settings

## What this library is responsible for

### Pin and timing configuration
Defined in `include/LeaderArmConfig.h`.

This includes:

- which analog pin belongs to each joint,
- how often angle data is sent to the PC.

### Calibration data types
Defined in `include/LeaderArmTypes.h`.

The key structure is `JointCalibration`, which stores:

- raw analog minimum,
- raw analog maximum,
- angle minimum in degrees,
- angle maximum in degrees.

### Default/fallback calibration
Defined in `include/LeaderArmDefaultCalibration.h`.

These values are used when no valid calibration is available in EEPROM.

### Reading and filtering inputs
Implemented in `src/LeaderArmReader.cpp`.

Responsibilities:

- average multiple analog samples,
- clamp values safely,
- convert raw analog values to calibrated angles.

### EEPROM settings
Declared in `include/LeaderArmSettings.h` and implemented in `src/LeaderArmSettings.cpp`.

Responsibilities:

- define the stored settings structure,
- load saved calibration from EEPROM,
- save calibration back to EEPROM,
- fall back to defaults when EEPROM is invalid or empty.

## Why this separation matters

Putting this logic in a shared library keeps the application entry points in `src/apps/` small and focused:

- `calibration.cpp` handles the user-guided calibration procedure,
- `stream_to_pc.cpp` handles runtime streaming.

## Licensing and attribution

- Code license (repository code): MIT (see [`../../LICENSE`](../../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../../LICENSE-MODEL.md`](../../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../../reference/permission-buildsomestuff.md`](../../reference/permission-buildsomestuff.md)
