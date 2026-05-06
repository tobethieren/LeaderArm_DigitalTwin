import json
import shutil
import socket
import subprocess
import sys
import time
from pathlib import Path

import serial
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
    # Eerst kijken of platformio/pio in PATH zit
    for candidate in ("platformio", "pio"):
        exe = shutil.which(candidate)
        if exe:
            return exe

    # Windows fallback
    windows_default = Path.home() / ".platformio" / "penv" / "Scripts" / "platformio.exe"
    if windows_default.exists():
        return str(windows_default)

    raise FileNotFoundError(
        "Kon PlatformIO niet vinden. Zorg dat PlatformIO geïnstalleerd is "
        "en dat 'platformio' of 'pio' beschikbaar is in PATH."
    )


def list_serial_ports():
    return list(list_ports.comports())


def choose_serial_port(config: dict) -> str:
    configured_port = str(config.get("serial_port", "auto")).strip()
    available_ports = list(list_ports.comports())

    if len(available_ports) == 0:
        raise RuntimeError("Geen seriële poorten gevonden.")

    # 1. Expliciete poort uit config
    if configured_port.lower() != "auto":
        available_names = [port.device for port in available_ports]
        if configured_port in available_names:
            print(f"Seriële poort uit config gebruikt: {configured_port}")
            return configured_port
        print(f"Waarschuwing: geconfigureerde poort {configured_port} is niet gevonden.")

    # 2. Automatisch Arduino-achtige poort zoeken
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

    # 3. Als er maar één poort is
    if len(available_ports) == 1:
        selected = available_ports[0].device
        print(f"Automatisch seriële poort gekozen: {selected}")
        return selected

    # 4. Anders manueel kiezen
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


def is_csv_angle_line(line: str) -> bool:
    parts = [part.strip() for part in line.split(",")]
    return len(parts) == 4 and all(is_float(part) for part in parts)


def read_eeprom_status(serial_port: str, baudrate: int, timeout: float = 4.0):
    """
    Probeert te detecteren of er een geldige calibratie in EEPROM zit.
    Werkt met:
    - EEPROM_STATUS:CALIBRATED
    - EEPROM_STATUS:DEFAULT
    - of de bestaande human-readable teksten uit stream_to_pc.cpp
    """
    print()
    print("=== EEPROM-status controleren ===")

    deadline = time.time() + timeout

    with serial.Serial(serial_port, baudrate, timeout=0.2) as ser:
        # Even tijd geven zodat de board kan opstarten
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

            # Numerieke stream-lijnen negeren
            if is_csv_angle_line(line):
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


def start_udp_stream(serial_port: str, baudrate: int, udp_ip: str, udp_port: int):
    print()
    print("=== Streaming naar Blender gestart ===")
    print(f"Serial: {serial_port} @ {baudrate}")
    print(f"UDP:    {udp_ip}:{udp_port}")
    print("Zorg dat Blender open staat en dat blender_udp_listener.py draait.")
    print("Stoppen: Ctrl+C")
    print()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        with serial.Serial(serial_port, baudrate, timeout=1) as ser:
            time.sleep(2.0)

            while True:
                raw = ser.readline()
                if not raw:
                    continue

                line = raw.decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                # Alleen echte 4-assen CSV-lijnen doorlaten
                parts = [part.strip() for part in line.split(",")]
                if len(parts) != 4 or not all(is_float(part) for part in parts):
                    print(f"Overslaan: {line!r}")
                    continue

                basis = float(parts[0])
                main = float(parts[1])
                fore = float(parts[2])
                wrist = float(parts[3])

                message = f"{basis:.2f},{main:.2f},{fore:.2f},{wrist:.2f}"
                sock.sendto(message.encode("utf-8"), (udp_ip, udp_port))

                print(
                    f"basis={basis:7.2f}  "
                    f"main={main:7.2f}  "
                    f"fore={fore:7.2f}  "
                    f"wrist={wrist:7.2f}",
                    end="\r"
                )

    except serial.SerialException as e:
        print()
        print(f"Kon seriële poort niet openen: {e}")
        print("Sluit eerst PlatformIO Serial Monitor / Arduino IDE / andere serial tools.")
    finally:
        sock.close()


def main():
    config = load_config()
    pio_exe = find_platformio()

    baudrate = int(config.get("baudrate", 115200))
    udp_ip = config.get("udp_ip", "127.0.0.1")
    udp_port = int(config.get("udp_port", 5005))
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

    # Eerst stream-firmware uploaden zodat we EEPROM-status kunnen opvragen
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

        # Na calibratie opnieuw stream-firmware uploaden
        run_platformio_upload(pio_exe, stream_env)
        print()
        print("Streaming-firmware opnieuw opgeladen.")
    else:
        print()
        print("Kalibratie overgeslagen.")

    print()
    input("Start nu in Blender de listener en druk hier Enter om de UDP-stream te starten...")

    start_udp_stream(serial_port, baudrate, udp_ip, udp_port)


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