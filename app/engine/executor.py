
from .models import WorkflowContext, ExecutionResult
from app.engine.handlers import HANDLERS


class WorkflowExecutor:
    def __init__(self, handlers=None):
        self.handlers = dict(
            HANDLERS if handlers is None else handlers
        )

    def register(self, workflow_id, handler):
        """Register a new workflow without changing this executor."""
        if workflow_id in self.handlers:
            raise ValueError(
                f"Handler already registered: {workflow_id}"
            )

        if not callable(handler):
            raise TypeError("Handler must be callable")

        self.handlers[workflow_id] = handler

    def execute(self, workflow, request, data):
        ctx = WorkflowContext(request, data)
        wid = workflow["id"]
        name = workflow.get("name", wid)

        handler = self.handlers.get(wid)

        if handler is None:
            message = f"Unsupported workflow: {wid}"
            ctx.log("Workflow dispatch", "error", message)
            return ExecutionResult(
                wid, name, 1, "FAILED",
                ctx.trace, None, message
            )

        try:
            ctx.log("Start workflow", detail=wid)

            result = handler(data, ctx)

            ctx.log("Workflow completed")

            return ExecutionResult(
                wid, name, 1, "SUCCESS",
                ctx.trace, result
            )

        except ValueError as e:
            ctx.log("Input validation", "error", str(e))

            return ExecutionResult(
                wid, name, 1, "NEEDS_INPUT",
                ctx.trace, None, str(e)
            )

        except Exception as e:
            ctx.log("Execution", "error", str(e))

            return ExecutionResult(
                wid, name, 1, "FAILED",
                ctx.trace, None, str(e)
            )
