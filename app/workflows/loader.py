import json
from pathlib import Path

class WorkflowRegistry:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.workflows = {w["id"]: w for w in json.loads(self.path.read_text())}

    def get(self, workflow_id: str):
        return self.workflows[workflow_id]

    def all(self):
        return list(self.workflows.values())
