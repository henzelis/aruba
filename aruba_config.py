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
s = Session(switch_ip, version)
s.open("admin", "admin")


switch = Device(s)

try:
    vsx = Vsx(s)
    vsx.get()
    print(f"VSX Device Role: {vsx.device_role}")
    print(f"VSX System MAC: {vsx.system_mac}")
    print(f"VSX ISL: {vsx.inter_switch_link}")
except Exception as e:
    print(f"VSX помилка: {e}")
    print("VSX НЕ налаштований - не можна використовувати vsx_sync!")


try:
    device = Device(s)
    vlan10 = Vlan(s, vlan_id=10)
    vlan10.get()
    print(f"vsx: {vlan10.vsx_sync}")
    print(f"Firmware: {device.firmware_version}")
    vlan101 = device.vlan(vlan_id=101, name="VLAN 101")
    vlan101.description = "VLAN101 TEST VLAN101"
    vlan101.vsx_sync = ['all_attributes_and_dependents']
    vlan101.apply()
    print("VLAN створено без vsx_sync")
    # switch.vlan.description = "VLAN100 by PyAOS-CX"
    # vsx = switch.vsx()
    # vsx.device_role = device_role
    # vsx.get()
    #
    # print(f"\nСтатус VSX:")
    # print(f"  - Роль: {vsx.device_role}")
    # print(f"  - System MAC: {vsx.system_mac}")
    # print(f"  - ISL порт: {vsx.isl_port}")
    # print(f"  - Keepalive peer IP: {vsx.keepalive_peer_ip}")

except Exception as error:
    print("Ran into exception: {0}. Closing session.".format(error))

finally:
    s.close()
