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
    if "loop" in step:
        return step["loop"]

    if "when" in step:
        key = step["when"]
        value = context["device_vars"].get(key)
        if isinstance(value, list):
            return value

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
            for step in job:
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


