import requests

class BiotechEnvClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def reset(self):
        return requests.post(f"{self.base_url}/reset").json()

    def step(self, action_type):
        return requests.post(
            f"{self.base_url}/step",
            json={"action_type": action_type}
        ).json()

    def state(self):
        return requests.get(f"{self.base_url}/state").json()