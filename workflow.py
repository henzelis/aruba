# workflow.py
from aruba_config_net import ArubaCXDevice
from tasks import TASK_REGISTRY


def run_job(devices, job, credentials, logger=print):
    for dev in devices:
        context = {
            "device_vars": dev,
            "logger": logger,
        }
        logger(f"Connecting to {dev['host']}")

        with ArubaCXDevice(
            dev["host"],
            credentials["username"],
            credentials["password"]
        ) as device:

            for step in job:
                task_fn = TASK_REGISTRY[step["task"]]
                task_fn(
                    device,
                    step["params"],
                    context
                )
