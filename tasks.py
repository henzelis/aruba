def vlan_task(device, params, context):
    cmds = device.build_vlan(
        vlan_id=params["id"],
        name=params.get("name"),
        description=params.get("description"),
    )
    if context["dry_run"]:
        context["logger"](f"[DRY-RUN] {cmds}")
        return {"changed": False, "dry_run": True}
    device.apply(cmds)
    return {"changed": True}


def svi_task(device,  params, context):
    vlan = params["id"]
    device_vars = context["device_vars"]
    svi_data = device_vars.get("svi", {}).get(vlan)
    if not svi_data:
        return
    cmds = device.build_svi(
        vlan_id=vlan,
        ip_address=svi_data["ip"],
        vrf=svi_data.get("vrf")
    )
    if context["dry_run"]:
        context["logger"](f"[DRY-RUN] {cmds}")
        return {"changed": False, "dry_run": True}
    device.apply(cmds)
    return {"changed": True}


def trunk_task(device, params, context):
    cmds = device.build_trunk(
        interface=params["interface"],
        allowed_vlans=params.get("allowed_vlans"),
        native_vlan=params.get("native_vlan")
    )
    if context["dry_run"]:
        context["logger"](f"[DRY-RUN] {cmds}")
        return {"changed": False, "dry_run": True}
    device.apply(cmds)
    return {"changed": True}


def active_gateway_task(device, params, context):
    cmds = device.build_active_gateway(
        vlan_id=params["vlan_id"],
        virtual_ip=params["virtual_ip"],
        mac=params.get("mac")
    )
    if context["dry_run"]:
        context["logger"](f"[DRY-RUN] {cmds}")
        return {"changed": False, "dry_run": True}
    device.apply(cmds)
    return {"changed": True}


def lag_task(device, params, context):
    cmds = device.build_lag(
        lag_id=params["lag_id"],
        ports=params["ports"],
        mode=params.get("mode", "active"),
        trunk=params.get("trunk", True),
        allowed_vlans=params.get("allowed_vlans"),
        multi_chassis=params.get("multi_chassis", False),
    )
    if context["dry_run"]:
        context["logger"](f"[DRY-RUN] {cmds}")
        return {"changed": False, "dry_run": True}
    device.apply(cmds)
    return {"changed": True}


def vsx_task(device, params, context):
    cmds = device.build_vsx(
        role=params["role"],
        system_mac=params["system_mac"],
        isl_lag=params["isl_lag"],
        keepalive_src=params["keepalive_src"],
        keepalive_peer=params["keepalive_peer"],
        vrf=params.get("vrf", "mgmt")
    )
    if context["dry_run"]:
        context["logger"](f"[DRY-RUN] {cmds}")
        return {"changed": False, "dry_run": True}
    device.apply(cmds)
    return {"changed": True}


TASK_REGISTRY = {
    "vlan": vlan_task,
    "svi": svi_task,
    "trunk": trunk_task,
    "active_gateway": active_gateway_task,
    "lag": lag_task,
    "vsx": vsx_task,
}
