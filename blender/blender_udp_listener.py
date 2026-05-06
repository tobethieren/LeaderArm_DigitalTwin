#blender_udp_listener.py
import bpy
import socket
import math

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
ARMATURE_NAME = "Armature"

STATE_KEY = "robot_udp_listener_4axis"

BONES = {
    "basis": {
        "bone_name": "BONE_BASIS",
        "axis": "Y",
        "invert": True,
        "offset_deg": 0.0,
    },
    "main": {
        "bone_name": "BONE_MAIN_ARM",
        "axis": "X",
        "invert": True,
        "offset_deg": 0.0,
    },
    "fore": {
        "bone_name": "BONE_FORE_ARM",
        "axis": "X",
        "invert": False,
        "offset_deg": 0.0,
    },
    "wrist": {
        "bone_name": "BONE_WRIST",
        "axis": "X",
        "invert": True,
        "offset_deg": 0.0,
    },
}

def stop_previous_listener():
    state = bpy.app.driver_namespace.get(STATE_KEY)
    if not state:
        return

    timer_fn = state.get("timer_fn")
    sock = state.get("sock")

    try:
        if timer_fn and bpy.app.timers.is_registered(timer_fn):
            bpy.app.timers.unregister(timer_fn)
    except Exception:
        pass

    try:
        if sock:
            sock.close()
    except Exception:
        pass

    bpy.app.driver_namespace.pop(STATE_KEY, None)
    print("Vorige 4-assen listener gestopt.")

def apply_angle_to_bone(pose_bone, axis, angle_deg, invert=False, offset_deg=0.0):
    pose_bone.rotation_mode = 'XYZ'

    final_deg = (-angle_deg if invert else angle_deg) + offset_deg
    angle_rad = math.radians(final_deg)

    if axis == "X":
        pose_bone.rotation_euler.x = angle_rad
    elif axis == "Y":
        pose_bone.rotation_euler.y = angle_rad
    elif axis == "Z":
        pose_bone.rotation_euler.z = angle_rad

def apply_angles(basis_deg, main_deg, fore_deg, wrist_deg):
    arm_obj = bpy.data.objects.get(ARMATURE_NAME)
    if arm_obj is None:
        print(f"Armature niet gevonden: {ARMATURE_NAME}")
        return

    if arm_obj.type != 'ARMATURE':
        print(f"Object '{ARMATURE_NAME}' is geen armature.")
        return

    values = {
        "basis": basis_deg,
        "main": main_deg,
        "fore": fore_deg,
        "wrist": wrist_deg,
    }

    for key, cfg in BONES.items():
        bone = arm_obj.pose.bones.get(cfg["bone_name"])
        if bone is None:
            print(f"Bone niet gevonden: {cfg['bone_name']}")
            continue

        apply_angle_to_bone(
            pose_bone=bone,
            axis=cfg["axis"],
            angle_deg=values[key],
            invert=cfg["invert"],
            offset_deg=cfg["offset_deg"],
        )

    bpy.context.view_layer.update()

def start_listener():
    stop_previous_listener()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    sock.setblocking(False)

    print(f"Luister op UDP {UDP_IP}:{UDP_PORT}")
    print(f"Armature = {ARMATURE_NAME}")
    print("4-assen Blender listener gestart.")

    def timer_callback():
        try:
            while True:
                data, _addr = sock.recvfrom(1024)
                text = data.decode("utf-8", errors="ignore").strip()
                if not text:
                    continue

                parts = text.split(",")
                if len(parts) != 4:
                    print(f"Ongeldige UDP payload: {text!r}")
                    continue

                basis_deg = float(parts[0])
                main_deg = float(parts[1])
                fore_deg = float(parts[2])
                wrist_deg = float(parts[3])

                apply_angles(basis_deg, main_deg, fore_deg, wrist_deg)

        except BlockingIOError:
            pass
        except ValueError:
            print(f"Kon UDP data niet parsen: {text!r}")
        except Exception as e:
            print(f"Fout in Blender listener: {e}")

        return 0.02

    bpy.app.driver_namespace[STATE_KEY] = {
        "sock": sock,
        "timer_fn": timer_callback,
    }

    bpy.app.timers.register(timer_callback)

start_listener()