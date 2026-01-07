from workflow import run_job
import yaml


def load_yaml(path):
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    inventory = load_yaml("inventory.yaml")
    job = load_yaml("jobs/job_2.yaml")

    devices = inventory["devices"]
    steps = job["steps"]

    credentials = {
        "username": "admin",
        "password": "admin",
    }

    run_job(devices, job, credentials)


if __name__ == "__main__":
    main()
