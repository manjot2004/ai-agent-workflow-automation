from dataclasses import dataclass, field
from typing import Any

@dataclass
class ExecutionResult:
    workflow_id: str
    workflow_name: str
    selected_confidence: float
    status: str
    steps: list[dict[str, Any]] = field(default_factory=list)
    result: Any = None
    error: str | None = None

@dataclass
class WorkflowContext:
    request: str
    data: dict[str, Any] = field(default_factory=dict)
    trace: list[dict[str, Any]] = field(default_factory=list)

    def log(self, step: str, status: str = "success", detail: str = ""):
        self.trace.append({"step": step, "status": status, "detail": detail})
