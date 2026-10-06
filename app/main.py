import argparse
import json
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from app.workflows.loader import WorkflowRegistry
from app.agent.agent import WorkflowAgent

app=typer.Typer()
console=Console()
ROOT=Path(__file__).resolve().parents[1]

def make_agent():
    return WorkflowAgent(WorkflowRegistry(ROOT/"config/workflows.json"))

def run_cli(request: str, workflow: str = "auto"):
    """Run the reusable workflow agent."""
    agent=make_agent()
    examples={
      "WF001":{"inventory_path":str(ROOT/"data/inventory.csv")},
      "WF002":{"product_path":str(ROOT/"data/products.csv"),"vendor_path":str(ROOT/"data/vendor_prices.csv")},
      "WF003":{"file_path":str(ROOT/"data/vendor_products.csv")},
      "WF004":{"product":{"product_name":"Trail Jacket","category":"Outdoor Jacket","attributes":"Water resistant","material":"Nylon","color":"Black","target_audience":"Hikers"}},
      "WF005":{"orders_path":str(ROOT/"data/orders.csv"),"order_id":"ORD-1001"},
      "WF006":{"catalog_path":str(ROOT/"data/catalog.csv")},
      "WF007":{"goal":"Launch the new collection","products":["Trail Jacket","Alpine Pack"],"audience":"Outdoor enthusiasts","promotion":"10% launch offer","dates":"2026-10-10 to 2026-10-20"},
      "WF008":{"keywords":["buy trail jacket","how to choose a hiking jacket","best hiking jackets","Trail Jacket"]},
      "WF009":{"employees_path":str(ROOT/"data/employees.csv"),"task":"Build the API integration","required_skills":["python","api"],"priority":"urgent"},
      "WF010":{"logs_path":str(ROOT/"data/execution_logs.csv")}
    }
    if workflow!="auto":
        w=agent.registry.get(workflow)
        data=examples[workflow]
        result=agent.executor.execute(w,request,data)
    else:
        w, confidence = agent.router.route(request)
        data=examples[w["id"]]
        result=agent.executor.execute(w,request,data)
        result.selected_confidence=confidence
    console.print(Panel(f"[bold]Selected Workflow:[/bold] {result.workflow_id} - {result.workflow_name}\nConfidence: {result.selected_confidence}"))
    console.print("[bold]Steps Executed:[/bold]")
    for i,s in enumerate(result.steps,1):
        console.print(f"{i}. {s['step']} [{s['status']}]")
    console.print(Panel(str(result.result),title=f"Result: {result.status}"))
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description="AI Agent Workflow Automation")
    parser.add_argument("request", help="Natural-language user request")
    parser.add_argument("--workflow", default="auto", help="Workflow ID or auto")
    args=parser.parse_args()
    run_cli(args.request,args.workflow)
