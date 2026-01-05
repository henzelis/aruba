# workflow.py
from aruba_config_net import ArubaCXDevice
from tasks import TASK_REGISTRY


def run_job(devices, job, credentials, logger=print):
    for dev in devices:
        logger(f"Connecting to {dev['host']}")

        with ArubaCXDevice(
            dev["host"],
            credentials["username"],
            credentials["password"]
        ) as device:

            for step in job:
                task_name = step["task"]
                params = step["params"]

                logger(f"Running {task_name} on {dev['host']}")
                TASK_REGISTRY[task_name](device, params)
