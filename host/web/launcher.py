import asyncio
import json
import shutil
import subprocess
import sys
import time
import os
import shlex
import webbrowser
from urllib.request import urlopen
from urllib.error import URLError
from pathlib import Path

import serial
import websockets
from serial.tools import list_ports


PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOST_DIR = Path(__file__).resolve().parent
CONFIG_PATH = HOST_DIR / "config.json"
EXAMPLE_CONFIG_PATH = HOST_DIR / "config.example.json"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    if EXAMPLE_CONFIG_PATH.exists():
        with open(EXAMPLE_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


def find_platformio() -> str:
    for candidate in ("platformio", "pio"):
        exe = shutil.which(candidate)
        if exe:
            return exe

    windows_default = Path.home() / ".platformio" / "penv" / "Scripts" / "platformio.exe"
    if windows_default.exists():
        return str(windows_default)

    raise FileNotFoundError(
        "Kon PlatformIO niet vinden. Zorg dat PlatformIO geïnstalleerd is "
        "en dat 'platformio' of 'pio' beschikbaar is in PATH."
    )


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


def run_platformio_upload(pio_exe: str, env_name: str):
    print()
    print(f"=== Uploading environment: {env_name} ===")

    command = [pio_exe, "run", "-e", env_name, "-t", "upload"]
    result = subprocess.run(command, cwd=PROJECT_ROOT)

    if result.returncode != 0:
        raise RuntimeError(f"Upload van environment '{env_name}' is mislukt.")


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"

    while True:
        answer = input(f"{prompt} {suffix} ").strip().lower()

        if answer == "":
            return default
        if answer in ("y", "yes", "j", "ja"):
            return True
        if answer in ("n", "no", "nee"):
            return False

        print("Gelieve Y of N in te geven.")


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


def read_eeprom_status(serial_port: str, baudrate: int, timeout: float = 4.0):
    print()
    print("=== EEPROM-status controleren ===")

    deadline = time.time() + timeout

    with serial.Serial(serial_port, baudrate, timeout=0.2) as ser:
        time.sleep(2.0)

        while time.time() < deadline:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            if line == "EEPROM_STATUS:CALIBRATED":
                print("EEPROM-status: geldige calibratie gevonden.")
                return True

            if line == "EEPROM_STATUS:DEFAULT":
                print("EEPROM-status: geen geldige calibratie gevonden.")
                return False

            if "Valid calibration loaded from EEPROM" in line:
                print("EEPROM-status: geldige calibratie gevonden.")
                return True

            if "No valid EEPROM calibration found" in line:
                print("EEPROM-status: geen geldige calibratie gevonden.")
                return False

            if parse_csv_angle_line(line) is not None:
                continue

            print(f"Info: {line}")

    print("EEPROM-status kon niet met zekerheid bepaald worden.")
    return None


def run_interactive_calibration(serial_port: str, baudrate: int):
    print()
    print("=== Interactieve kalibratie gestart ===")
    print("Volg de instructies hieronder.")
    print()

    with serial.Serial(serial_port, baudrate, timeout=0.2) as ser:
        time.sleep(2.0)

        while True:
            raw = ser.readline()
            if not raw:
                continue

            line = raw.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            print(line)

            if "druk Enter" in line or "druk enter" in line.lower():
                input("Zet de as in de gevraagde positie en druk hier Enter...")
                ser.write(b"\n")
                ser.flush()

            if "Kalibratie opgeslagen in EEPROM." in line:
                print()
                print("Kalibratie succesvol afgerond.")
                return


def start_websocket_stream(serial_port: str, baudrate: int, ws_host: str, ws_port: int):
    async def run_server():
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

            print()
            print("=== Streaming naar website gestart ===")
            print(f"Serial:    {serial_port} @ {baudrate}")
            print(f"WebSocket: ws://{ws_host}:{ws_port}")
            print("Open je website en laat die verbinden met deze WebSocket.")
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
                        print(f"Overslaan: {line!r}")
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

        async with websockets.serve(ws_handler, ws_host, ws_port):
            print(f"WebSocket server running on ws://{ws_host}:{ws_port}")
            await serial_loop()

    try:
        asyncio.run(run_server())
    except serial.SerialException as e:
        print()
        print(f"Kon seriële poort niet openen: {e}")
        print("Sluit eerst PlatformIO Serial Monitor / Arduino IDE / andere serial tools.")

def resolve_web_dir(config: dict) -> Path:
    raw = str(config.get("web_dir", "../../web")).strip()
    web_dir = (HOST_DIR / raw).resolve()
    if not web_dir.exists():
        raise FileNotFoundError(f"Web directory niet gevonden: {web_dir}")
    return web_dir


def start_website_process(config: dict):
    web_dir = resolve_web_dir(config)
    web_command = str(config.get("web_command", "npm run dev")).strip()

    print()
    print("=== Website starten ===")
    print(f"Map:     {web_dir}")
    print(f"Command: {web_command}")

    # shell=True is easiest on Windows for npm commands
    process = subprocess.Popen(
        web_command,
        cwd=web_dir,
        shell=True
    )

    return process


def wait_for_web_server(web_url: str, timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout

    while time.time() < deadline:
        try:
            with urlopen(web_url, timeout=1.5) as response:
                if 200 <= getattr(response, "status", 200) < 500:
                    return True
        except URLError:
            pass
        except Exception:
            pass

        time.sleep(0.5)

    return False


def maybe_start_website(config: dict):
    auto_start_website = bool(config.get("auto_start_website", False))
    auto_open_browser = bool(config.get("auto_open_browser", False))
    web_url = str(config.get("web_url", "http://127.0.0.1:5173")).strip()

    if not auto_start_website:
        return None

    process = start_website_process(config)

    print(f"Wachten tot website beschikbaar is op {web_url} ...")
    is_ready = wait_for_web_server(web_url, timeout=25.0)

    if is_ready:
        print("Website is gestart.")
        if auto_open_browser:
            try:
                webbrowser.open(web_url)
                print(f"Browser geopend: {web_url}")
            except Exception as e:
                print(f"Kon browser niet automatisch openen: {e}")
    else:
        print("Waarschuwing: website lijkt nog niet bereikbaar.")
        print("Controleer of npm install is uitgevoerd en of de dev server correct start.")

    return process


def main():
    config = load_config()
    pio_exe = find_platformio()
    website_process = None

    baudrate = int(config.get("baudrate", 115200))
    ws_host = str(config.get("ws_host", "127.0.0.1"))
    ws_port = int(config.get("ws_port", 8765))
    stream_env = config.get("stream_env", "stream_to_pc")
    calibration_env = config.get("calibration_env", "calibration")

    print("======================================")
    print(" Leader Arm Launcher")
    print("======================================")
    print()

    serial_port = choose_serial_port(config)
    print(f"Gekozen seriële poort: {serial_port}")

    print()
    print("Belangrijk: sluit PlatformIO Serial Monitor voordat je verdergaat.")
    input("Druk Enter om verder te gaan...")

    run_platformio_upload(pio_exe, stream_env)

    status = read_eeprom_status(serial_port, baudrate)

    if status is True:
        print("Er is al een geldige calibratie aanwezig in EEPROM.")
        should_calibrate = ask_yes_no("Wil je opnieuw kalibreren?", default=False)
    elif status is False:
        print("Er is nog geen geldige calibratie aanwezig in EEPROM.")
        should_calibrate = ask_yes_no("Wil je nu kalibreren?", default=True)
    else:
        print("De status kon niet zeker bepaald worden.")
        should_calibrate = ask_yes_no("Wil je toch kalibreren?", default=False)

    if should_calibrate:
        run_platformio_upload(pio_exe, calibration_env)
        run_interactive_calibration(serial_port, baudrate)

        run_platformio_upload(pio_exe, stream_env)
        print()
        print("Streaming-firmware opnieuw opgeladen.")
    else:
        print()
        print("Kalibratie overgeslagen.")

    print()
    website_process = maybe_start_website(config)

    print()
    print("WebSocket-stream wordt gestart...")
    start_websocket_stream(serial_port, baudrate, ws_host, ws_port)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("\nLauncher gestopt.")
    except Exception as e:
        print()
        print(f"Fout: {e}")
        sys.exit(1)