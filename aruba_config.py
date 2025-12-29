import urllib3
import time
import gc
from pyaoscx.session import Session
from pyaoscx.pyaoscx_factory import PyaoscxFactory
from pyaoscx.vlan import Vlan
from pyaoscx.device import Device
from pyaoscx.interface import Interface
from pyaoscx.vsx import Vsx

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

version = "10.04"
switch_ip = "192.168.109.10"
# s = Session(switch_ip, version)
# s.open("admin", "admin")
# switch = Device(s)

VLANS_TO_CREATE = [
    {"id": 10, "name": "VLAN_USERS", "description": "User VLAN", "vsx": True},
    {"id": 20, "name": "VLAN_SERVERS", "description": "Server VLAN", "vsx": True},
    {"id": 30, "name": "VLAN_GUESTS", "description": "Guest VLAN", "vsx": True},
    {"id": 40, "name": "VLAN_MANAGEMENT", "description": "Management VLAN", "vsx": True},
]

VSX_PARAM = [
    {"switch_ip": "192.168.109.10", "vsx_role": "primary", "keepalive_ip": "169.254.254.1",
     "keepalive_peer_ip": "169.254.254.2", "isl_lag_id": "254", "isl_ports": ["1/1/2", "1/1/3"],
     'vsx_mac': '02:01:00:00:01:00'},
    {"switch_ip": "192.168.109.11", "vsx_role": "secondary", "keepalive_ip": "169.254.254.2",
     "keepalive_peer_ip": "169.254.254.1", "isl_lag_id": "254", "isl_ports": ["1/1/2", "1/1/3"],
     'vsx_mac': '02:00:00:00:01:00'},
]


def create_vsx(device, isl_lag_id, isl_ports, keepalive_ip=None, keepalive_peer_ip=None, vsx_role=None, vsx_mac=None):
    try:
        lag_name = f"lag{isl_lag_id}"
        isl_lag = device.interface(lag_name)
        isl_lag.configure_l2()
        isl_lag.admin_state = "up"
        isl_lag.interfaces = isl_ports
        isl_lag.update()
        isl_lag.get()
        print(f'{lag_name} - created successfully')
        print(f'Port {isl_ports} added to {lag_name}')
        vsx = device.vsx(
            device_role=vsx_role,
            system_mac=vsx_mac,
            isl_port=lag_name,
            keepalive_peer_ip=keepalive_peer_ip,
            keepalive_src_ip=keepalive_ip,
            keepalive_vrf="mgmt"
        )
        vsx.get()
        print(f'VSX configured with port {lag_name}, role - {vsx_role}')
    except Exception as error:
        print(f"Ran into exception: {error}. Closing session")


def create_vlan(device, vlan_id, vlan_name=None, vlan_description=None, vsx_syncronization=False):
    try:
        config_vlan = device.vlan(vlan_id=vlan_id, name=vlan_name)
        config_vlan.description = vlan_description
        if vsx_syncronization:
            config_vlan.vsx_sync = ['all_attributes_and_dependents']
        config_vlan.apply()
    except Exception as error:
        print("Ran into exception: {0}. Closing session.".format(error))


# try:
#     s = Session(switch_ip, version)
#     s.open("admin", "admin")
#     vsx = Vsx(s)
#     vsx.get()
#     print(f"VSX Device Role: {vsx.device_role}")
#     print(f"VSX System MAC: {vsx.system_mac}")
#     print(f"VSX ISL: {vsx.isl_port}")
# except Exception as e:
#     print(f"VSX помилка: {e}")
#     print("VSX НЕ налаштований - не можна використовувати vsx_sync!")
# finally:
#     s.close()

def verify_session_closed(session):
    """
    Перевірка чи сесія закрита
    """
    try:
        # Спроба доступу до сесії
        if hasattr(session, 's') and session.s is not None:
            print("  ⚠ Session object still exists")
            return False
        print("  ✓ Session closed successfully")
        return True
    except:
        print("  ✓ Session closed successfully")
        return True


def force_close_session(session):
    """
    Примусове закриття сесії з перевіркою
    """
    print("\n  Closing session...")
    try:
        session.close()
        print("  session.close() called")
    except Exception as e:
        print(f"  Error during close: {e}")

    # Примусове видалення внутрішніх об'єктів
    try:
        if hasattr(session, 's'):
            session.s = None
        if hasattr(session, 'session'):
            session.session = None
    except:
        pass

    verify_session_closed(session)


if __name__ == "__main__":
    # for vlan in VLANS_TO_CREATE:
    #     create_vlan(vlan_id=vlan['id'], vlan_name=vlan['name'], vlan_description=vlan['description'], vsx_syncronization=vlan['vsx'])
    #     print(f'FOR VLAN{vlan["id"]} - JOB IS DONE! ')
    # sessions = []
    # for switch in VSX_PARAM:
    #     s = Session(switch['switch_ip'], version)
    #     s.open("admin", "admin")
    #     sessions.append(s)
    # for i, switch in enumerate(VSX_PARAM):
    #     create_vsx(sessions[i], isl_lag_id=switch['isl_lag_id'], isl_ports=switch['isl_ports'],
    #                keepalive_ip=switch['keepalive_ip'], keepalive_peer_ip=switch["keepalive_peer_ip"],
    #                vsx_role=switch['vsx_role'], vsx_mac=switch['vsx_mac'])
    # for s in sessions:
    #     s.close()
    for i, switch_params in enumerate(VSX_PARAM):
        s = None
        device = None
        try:
            print(f"\n{'=' * 70}")
            print(
                f"[{i + 1}/{len(VSX_PARAM)}] Configuring VSX on {switch_params['switch_ip']} ({switch_params['vsx_role']})")
            print(f"{'=' * 70}\n")

            print(f"  Opening session to {switch_params['switch_ip']}...")
            s = Session(switch_params['switch_ip'], version)
            s.open("admin", "admin")
            print(f"  ✓ Session opened successfully")

            # Примусове очищення пам'яті
            # gc.collect()

            # Створюємо Device
            print(f"  Creating Device object...")
            device = Device.__new__(Device)  # Створюємо новий екземпляр без __init__
            device.__init__(s)  # Викликаємо __init__ явно
            print(f"  Device object created: {device} at {id(device)}")

            # Конфігурація
            create_vsx(
                device=device,
                isl_lag_id=switch_params['isl_lag_id'],
                isl_ports=switch_params['isl_ports'],
                keepalive_ip=switch_params['keepalive_ip'],
                keepalive_peer_ip=switch_params['keepalive_peer_ip'],
                vsx_role=switch_params['vsx_role'],
                vsx_mac=switch_params['vsx_mac']
            )

            print(f"\n✓ Finished configuring {switch_params['switch_ip']}")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback

            traceback.print_exc()

        finally:
            if s is not None:
                force_close_session(s)

            # Примусове видалення всіх посилань
            if device is not None:
                del device
            if s is not None:
                del s

            # Примусове очищення garbage collector
            gc.collect()

            if i < len(VSX_PARAM) - 1:
                print(f"\n  Waiting 5 seconds before next switch...")
                time.sleep(5)