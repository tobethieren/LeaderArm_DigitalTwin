# Host workflow for the web viewer

This folder contains the host-side scripts for the **browser-based workflow**.

## Files

- `launcher.py` – complete guided launcher for the web route
- `serial_to_websocket.py` – serial-to-WebSocket bridge
- `config.example.json` – example configuration
- `config.json` – local configuration used on the current machine

## Main workflow

The typical entry point is `launcher.py`.

It performs the following steps:

1. load local configuration,
2. find PlatformIO,
3. choose the serial port,
4. upload `stream_to_pc` firmware,
5. inspect EEPROM calibration state,
6. optionally run the interactive calibration app,
7. optionally start the website,
8. stream joint angles to the browser over WebSocket.

## WebSocket bridge

`serial_to_websocket.py`:

- reads serial CSV lines from the microcontroller,
- validates that each line contains four numeric values,
- converts the angles to JSON,
- broadcasts the latest payload to connected browser clients.

Payload shape:

```json
{
  "basis": 0.0,
  "main": 0.0,
  "fore": 0.0,
  "wrist": 0.0
}
```

Default WebSocket endpoint:

```text
ws://127.0.0.1:8765
```

That default matches the browser-side code in `web/src/main.js`.

## Website startup support

The launcher can optionally start the Vite dev server automatically.

Relevant config keys:

- `auto_start_website`
- `web_dir`
- `web_command`
- `web_url`
- `auto_open_browser`

This is useful for demos, because one command can start both the host bridge and the website.

## Licensing and attribution

- Code license (repository code): MIT (see [`../../LICENSE`](../../LICENSE))
- Model asset license: CC BY-NC-ND 4.0 + cascading credit (see [`../../LICENSE-MODEL.md`](../../LICENSE-MODEL.md))
- Permission record for academic sharing: [`../../reference/permission-buildsomestuff.md`](../../reference/permission-buildsomestuff.md)
