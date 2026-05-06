# Host workflow for Blender

This folder contains the host-side scripts for the **Blender route**.

## Files

- `launcher.py` – complete guided launcher for the Blender workflow
- `serial_to_udp_brigde.py` – smaller bridge script that forwards serial angle data to UDP
- `config.example.json` – example configuration
- `config.json` – local configuration used on the current machine

## Main workflow

The typical entry point is `launcher.py`.

It performs the following steps:

1. load local configuration,
2. find PlatformIO,
3. choose the serial port,
4. upload `stream_to_pc` firmware,
5. inspect the EEPROM calibration status,
6. optionally upload and run the calibration app,
7. start streaming serial data to Blender over UDP.

## UDP bridge

The bridge forwards lines in this format:

```text
basis,main,fore,wrist
```

to the UDP endpoint configured in `config.json`.

Default values:

- IP: `127.0.0.1`
- port: `5005`

Those defaults match `blender/blender_udp_listener.py`.

## Configuration

`config.example.json` documents the available settings:

- `serial_port`
- `baudrate`
- `udp_ip`
- `udp_port`
- `stream_env`
- `calibration_env`

For a public repository, keep `config.example.json` as the template and adapt `config.json` locally per machine.

## Licensing and attribution

- Code license (repository code): MIT (see [`../../LICENSE`](../../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../../LICENSE-MODEL.md`](../../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../../reference/permission-buildsomestuff.md`](../../reference/permission-buildsomestuff.md)
