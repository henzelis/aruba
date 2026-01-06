def vlan_task(device, params, context):
    device.configure_vlan(
        vlan_id=params["id"],
        name=params.get("name"),
        description=params.get("description"),
    )


def svi_task(device,  params, context):
    vlan = params["vlan"]
    device_vars = context["device_vars"]
    svi_data = device_vars.get("svi", {}).get(vlan)
    if not svi_data:
        return
    device.configure_svi(
        vlan_id=vlan,
        ip_address=svi_data["ip"],
        vrf=svi_data.get("vrf")
    )


def trunk_task(device, params, context):
    device.configure_trunk(
        interface=params["interface"],
        allowed_vlans=params.get("allowed_vlans"),
        native_vlan=params.get("native_vlan")
    )


def active_gateway_task(device, params, context):
    device.configure_active_gateway(
        vlan_id=params["vlan_id"],
        virtual_ip=params["virtual_ip"],
        mac=params.get("mac")
    )


def lag_task(device, params, context):
    device.configure_lag(
        lag_id=params["lag_id"],
        ports=params["ports"],
        mode=params.get("mode", "active"),
        trunk=params.get("trunk", True),
        allowed_vlans=params.get("allowed_vlans"),
        multi_chassis=params.get("multi_chassis", False),
    )


def vsx_task(device, params, context):
    device.configure_vsx(
        role=params["role"],
        system_mac=params["system_mac"],
        isl_lag=params["isl_lag"],
        keepalive_src=params["keepalive_src"],
        keepalive_peer=params["keepalive_peer"],
        vrf=params.get("vrf", "mgmt")
    )


TASK_REGISTRY = {
    "vlan": vlan_task,
    "svi": svi_task,
    "trunk": trunk_task,
    "active_gateway": active_gateway_task,
    "lag": lag_task,
    "vsx": vsx_task,
}
