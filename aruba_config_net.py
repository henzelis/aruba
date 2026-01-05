from netmiko import ConnectHandler

VSX_PARAM = [
    {
        "host": "192.168.109.10",
        "role": "primary",
        "mac": "02:01:00:00:01:00",
        "src": "169.254.254.1",
        "peer": "169.254.254.2",
        "isl": 254,
        "ports": ["1/1/2", "1/1/3"],
    },
    {
        "host": "192.168.109.11",
        "role": "secondary",
        "mac": "02:00:00:00:01:00",
        "src": "169.254.254.2",
        "peer": "169.254.254.1",
        "isl": 254,
        "ports": ["1/1/2", "1/1/3"],
    },
]

VLANS_TO_CREATE = [
    {"id": 10, "name": "VLAN_USERS", "description": "User VLAN", "vsx": True},
    {"id": 20, "name": "VLAN_SERVERS", "description": "Server VLAN", "vsx": True},
    {"id": 30, "name": "VLAN_GUESTS", "description": "Guest VLAN", "vsx": True},
    {"id": 40, "name": "VLAN_MANAGEMENT", "description": "Management VLAN", "vsx": True},
]

SVI = {
    "sw1": {
        "mgmt_ip": "192.168.109.10",
        "svi": [
            {"id": "10",
             "ip": "10.10.10.2/24",
             "active_gateway": True,
             "virtual_ip": "10.10.10.1",
             "mac": "12:01:00:00:01:00"},
        ]
    },
    "sw2": {
        "mgmt_ip": "192.168.109.11",
        "svi": [
            {"id": "10", "ip": "10.10.10.3/24",
             "active_gateway": True,
             "virtual_ip": "10.10.10.1",
             "mac": "12:01:00:00:01:00"},
        ]
    }
}


class ArubaCXDevice:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.conn = None

    def connect(self):
        self.conn = ConnectHandler(
            device_type="aruba_aoscx",
            host=self.host,
            username=self.username,
            password=self.password
        )
        return self

    def disconnect(self):
        if self.conn:
            self.conn.disconnect()
            self.conn = None

    def send_config(self, commands):
        if not self.conn:
            raise RuntimeError("Device not connected")
        return self.conn.send_config_set(commands)

    def send_show(self, command):
        if not self.conn:
            raise RuntimeError("Device not connected")
        return self.conn.send_command(command)

    def __enter__(self):
        return self.connect()

    def __exit__(self, exc_type, exc, tb):
        self.disconnect()

    def configure_vlan(self, vlan_id, name=None, description=None, vsx_sync=False):
        cmds = [f"vlan {vlan_id}"]
        if name:
            cmds.append(f"name {name}")
        if description:
            cmds.append(f"description {description}")
        if vsx_sync:
            cmds.append(f"vsx-sync")
        return self.send_config(cmds)

    def configure_svi(self, vlan_id, ip_address, vrf=None):
        cmds = [
            f"interface vlan {vlan_id}",
            f"ip address {ip_address}",
            "no shutdown"
        ]

        if vrf:
            cmds.append(f"vrf attach {vrf}")

        return self.send_config(cmds)

    def configure_active_gateway(self, vlan_id, virtual_ip, mac=None):
        cmds = [
            f"interface vlan {vlan_id}",
            "vsx-sync active-gateways",
            f"active-gateway ip {virtual_ip}",
        ]

        if mac:
            cmds.append(f"active-gateway ip mac {mac}")

        return self.send_config(cmds)

    def configure_lag(self, lag_id, ports, mode="active", trunk=True, allowed_vlans=None, multi_chassis=False):
        if multi_chassis:
            cmds = [
                f"interface lag {lag_id} multi-chassis",
                "no shutdown",
                "no routing",
                f"lacp mode {mode}"
            ]
        else:
            cmds = [
                f"interface lag {lag_id}",
                "no shutdown",
                "no routing",
                f"lacp mode {mode}"
            ]
        if trunk:
            cmds.append("vlan trunk")
            if allowed_vlans:
                cmds.append(f"vlan trunk allowed {allowed_vlans}")
        else:
            cmds.append("vlan access")
        for port in ports:
            cmds.append(f"interface {port}")
            cmds.append(f"lag {lag_id}")
            cmds.append("no shutdown")

        return self.send_config(cmds)

    def configure_trunk(self, interface, allowed_vlans="all", native_vlan=None):
        cmds = [
            f"interface {interface}",
            "vlan trunk"
        ]
        if allowed_vlans != "all":
            cmds.append(f"vlan trunk allowed {allowed_vlans}")
        else:
            cmds.append(f"vlan trunk allowed all")
        if native_vlan:
            cmds.append(f"vlan trunk native {native_vlan}")

        return self.send_config(cmds)

    def configure_vsx(self, role, system_mac, isl_lag, keepalive_src, keepalive_peer, vrf="mgmt"):
        cmds = [
            "vsx",
            f"system-mac {system_mac}",
            f"inter-switch-link lag {isl_lag}",
            f"role {role}",
            f"keepalive peer {keepalive_peer} source {keepalive_src} vrf {vrf}",
            "vsx-sync vsx-global"
        ]

        return self.send_config(cmds)


if __name__ == "__main__":

    for sw in VSX_PARAM:
        with ArubaCXDevice(sw["host"], "admin", "admin") as dev:
            dev.create_lag(sw["isl"], sw["ports"])
            dev.configure_vsx(
                role=sw["role"],
                system_mac=sw["mac"],
                isl_lag=sw["isl"],
                keepalive_src=sw["src"],
                keepalive_peer=sw["peer"],
            )
    for sw, sw_data in SVI.items():
        mgmt_ip = sw_data["mgmt_ip"]
        with ArubaCXDevice(mgmt_ip, "admin", "admin") as dev:
            for svi in sw_data["svi"]:
                vlan_id = svi["id"]
                vlan_ip = svi["ip"]
                dev.configure_svi(vlan_id, vlan_ip)
                print(f"{sw} ({mgmt_ip})): VLAN {vlan_id} -> {vlan_ip}")
                if svi["active_gateway"]:
                    virtual_ip = svi["virtual_ip"]
                    mac = svi["mac"]
                    dev.configure_active_gateway(vlan_id, virtual_ip, mac)
                    print(f"{sw}: VLAN {vlan_id} -> Active Gateway ({virtual_ip}, {mac})")
