import urllib3

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
    {"switch_ip": "192.168.109.10", "keepalive_ip": "169.254.254.1", "keealive_peer_ip": "169.254.254.2", "isl_lag_id": "254","isl_ports": ["1/1/49", "1/1/50"]},
    {"switch_ip": "192.168.109.11", "keepalive_ip": "169.254.254.2", "keealive_peer_ip": "169.254.254.1", "isl_lag_id": "254","isl_ports": ["1/1/49", "1/1/50"]},
]


def create_vsx(session, isl_lag_id, isl_ports, keeaplive_ip=None, keepalive_peer_ip=None):
    try:
        device = Device(session)
        lag_name = f"lag{isl_lag_id}"
        isl_lag = device.interface(lag_name)
        isl_lag.configure_l2()
        isl_lag.admin_state = "up"
        isl_lag.apply()
        isl_lag.get()
        print(f'{lag_name} - created successfully')
        for port in isl_ports:
            isl_lag.interfaces.append(port)
            isl_lag.apply()
            print(f'Port {port} added to {lag_name}')
    except Exception as error:
        print("Ran into exception: {0}. Closing session.".format(error))


def create_vlan(session, vlan_id, vlan_name=None, vlan_description=None, vsx_syncronization=False):
    try:
        device = Device(session)
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


if __name__ == "__main__":
    # for vlan in VLANS_TO_CREATE:
    #     create_vlan(vlan_id=vlan['id'], vlan_name=vlan['name'], vlan_description=vlan['description'], vsx_syncronization=vlan['vsx'])
    #     print(f'FOR VLAN{vlan["id"]} - JOB IS DONE! ')
    for switch in VSX_PARAM:
        s = Session(switch['switch_ip'], version)
        s.open("admin", "admin")
        create_vsx(s, isl_lag_id=switch['isl_lag_id'], isl_ports=switch['isl_ports'])
        s.close()
