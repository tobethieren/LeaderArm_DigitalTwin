import asyncio
import json
import time
from pathlib import Path

import serial
import websockets
from serial.tools import list_ports


SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "config.json"
EXAMPLE_CONFIG_PATH = SCRIPT_DIR / "config.example.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    if EXAMPLE_CONFIG_PATH.exists():
        with open(EXAMPLE_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def parse_csv_angle_line(line: str):
    parts = [part.strip() for part in line.split(",")]
    if len(parts) != 4 or not all(is_float(part) for part in parts):
        return None
    return tuple(float(part) for part in parts)


def choose_serial_port(config: dict) -> str:
    configured_port = str(config.get("serial_port", "auto")).strip()
    available_ports = list(list_ports.comports())

    if len(available_ports) == 0:
        raise RuntimeError("Geen seriële poorten gevonden.")

    if configured_port.lower() != "auto":
        available_names = [port.device for port in available_ports]
        if configured_port in available_names:
            print(f"Seriële poort uit config gebruikt: {configured_port}")
            return configured_port
        print(f"Waarschuwing: geconfigureerde poort {configured_port} is niet gevonden.")

    preferred_ports = []
    for port in available_ports:
        description = (port.description or "").lower()
        manufacturer = (port.manufacturer or "").lower()

        if (
            "arduino" in description
            or "arduino" in manufacturer
            or "usb serial" in description
            or "ch340" in description
            or "cp210" in description
        ):
            preferred_ports.append(port)

    if len(preferred_ports) == 1:
        selected = preferred_ports[0].device
        print(f"Automatisch Arduino-poort gekozen: {selected}")
        return selected

    if len(available_ports) == 1:
        selected = available_ports[0].device
        print(f"Automatisch seriële poort gekozen: {selected}")
        return selected

    print("Beschikbare seriële poorten:")
    for idx, port in enumerate(available_ports, start=1):
        print(f"  {idx}. {port.device} - {port.description}")

    while True:
        choice = input("Kies het nummer van de Arduino-poort: ").strip()
        if choice.isdigit():
            index = int(choice) - 1
            if 0 <= index < len(available_ports):
                selected = available_ports[index].device
                print(f"Handmatig gekozen poort: {selected}")
                return selected
        print("Ongeldige keuze. Probeer opnieuw.")


async def main():
    config = load_config()
    serial_port = choose_serial_port(config)
    baudrate = int(config.get("baudrate", 115200))
    ws_host = str(config.get("ws_host", "127.0.0.1"))
    ws_port = int(config.get("ws_port", 8765))

    clients = set()
    last_payload = None

    async def broadcast(message: str):
        dead = []
        for ws in tuple(clients):
            try:
                await ws.send(message)
            except Exception:
                dead.append(ws)

        for ws in dead:
            clients.discard(ws)

    async def ws_handler(websocket):
        nonlocal last_payload
        clients.add(websocket)
        print(f"\nBrowser connected ({len(clients)} client(s))")

        try:
            if last_payload is not None:
                await websocket.send(last_payload)
            await websocket.wait_closed()
        finally:
            clients.discard(websocket)
            print(f"\nBrowser disconnected ({len(clients)} client(s) left)")

    async def serial_loop():
        nonlocal last_payload

        print(f"Open serial on {serial_port} @ {baudrate}")
        print(f"WebSocket server running on ws://{ws_host}:{ws_port}")
        print("Stoppen: Ctrl+C")
        print()

        with serial.Serial(serial_port, baudrate, timeout=1) as ser:
            time.sleep(2.0)

            while True:
                raw = await asyncio.to_thread(ser.readline)
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                angles = parse_csv_angle_line(line)
                if angles is None:
                    print(f"Skipping: {line!r}")
                    continue

                basis, main, fore, wrist = angles

                last_payload = json.dumps({
                    "basis": basis,
                    "main": main,
                    "fore": fore,
                    "wrist": wrist,
                })

                await broadcast(last_payload)

                print(
                    f"basis={basis:7.2f}  "
                    f"main={main:7.2f}  "
                    f"fore={fore:7.2f}  "
                    f"wrist={wrist:7.2f}",
                    end="\r",
                    flush=True
                )

    try:
        async with websockets.serve(ws_handler, ws_host, ws_port):
            await serial_loop()
    except serial.SerialException as e:
        print()
        print(f"Kon seriële poort niet openen: {e}")
        print("Sluit eerst PlatformIO Serial Monitor / Arduino IDE / andere serial tools.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped.")