# workflow.py
from aruba_config_net import ArubaCXDevice
from tasks import TASK_REGISTRY


def should_run(step, context):
    condition = step.get("when")
    if not condition:
        return True

    device_vars = context["device_vars"]
    return condition in device_vars


def extend_loop(step, context):
    device_vars = context["device_vars"]

    # 🔹 case 1: loop + when + inventory dict  → MERGE
    if "loop" in step and "when" in step:
        key = step["when"]
        inventory_value = device_vars.get(key)

        if isinstance(inventory_value, dict):
            items = []
            for loop_item in step["loop"]:
                item_id = loop_item.get("id")
                if item_id not in inventory_value:
                    continue  # або raise, якщо хочеш strict

                merged = {"id": item_id}
                merged.update(inventory_value[item_id])
                merged.update(loop_item)  # loop може override-ити
                items.append(merged)

            return items

    # 🔹 case 2: явний loop без inventory
    if "loop" in step:
        return step["loop"]

    # 🔹 case 3: inventory list або dict без loop
    if "when" in step:
        key = step["when"]
        value = device_vars.get(key)

        if isinstance(value, list):
            return value

        if isinstance(value, dict):
            return [
                {"id": k, **v}
                for k, v in value.items()
            ]

    # 🔹 fallback
    return [step.get("params", {})]


def run_job(devices, job, credentials, logger=print):
    fail_fast = job.get("fail_fast", False)
    for dev in devices:
        context = {
            "device_vars": dev,
            "dry_run": True,
            "logger": logger,
        }
        logger(f"Connecting to {dev['host']}")

        with ArubaCXDevice(
            dev["host"],
            credentials["username"],
            credentials["password"]
        ) as device:
            steps = job["steps"]
            for step in steps:
                if not should_run(step, context):
                    context["logger"](f"SKIPPED {step['task']} on {device.host}")
                    continue
                task_fn = TASK_REGISTRY[step["task"]]

                items = extend_loop(step, context)

                for item in items:
                    params = step.get("params", {})
                    params = {**params, **item}
                    try:
                        result = task_fn(device, params, context)
                        results = [result]

                    except Exception as exc:
                        context["logger"](f"ERORR on {device.host} task={step['task']} params={params}: {exc}")

                        errors =[{
                            "device": device.host,
                            "task": step["task"],
                            "params": params,
                            "error": str(exc),
                        }]

                        if fail_fast == "task":
                            break  # вихід з loop

                        if fail_fast == "job":
                            raise

                        continue


