import json
import socket
import time
from pathlib import Path

import serial
from serial.tools import list_ports


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


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def main():
    config = load_config()

    serial_port = choose_serial_port(config)
    baudrate = int(config.get("baudrate", 115200))
    udp_ip = config.get("udp_ip", "127.0.0.1")
    udp_port = int(config.get("udp_port", 5005))

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print(f"Open serial op {serial_port} @ {baudrate}")
    print(f"Stuur UDP naar {udp_ip}:{udp_port}")

    try:
        with serial.Serial(serial_port, baudrate, timeout=1) as ser:
            time.sleep(2.0)  # geef de board even tijd na openen

            while True:
                line = ser.readline().decode("utf-8", errors="ignore").strip()
                if not line:
                    continue

                parts = [part.strip() for part in line.split(",")]
                if len(parts) != 4 or not all(is_float(part) for part in parts):
                    print(f"Ongeldige lijn (verwacht 4 floats): {line!r}")
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
        print(f"Kon serial poort niet openen: {e}")
        print("Sluit eerst PlatformIO Serial Monitor / Arduino IDE / andere serial tools.")
    finally:
        sock.close()


if __name__ == "__main__":
    main()