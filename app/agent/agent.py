from app.agent.router import WorkflowRouter
from app.engine.executor import WorkflowExecutor

class WorkflowAgent:
    def __init__(self, registry, llm=None):
        self.registry=registry
        self.router=WorkflowRouter(registry.all(), llm)
        self.executor=WorkflowExecutor()

    def run(self, request, data):
        workflow, confidence=self.router.route(request)
        result=self.executor.execute(workflow,request,data)
        result.selected_confidence=confidence
        return result
