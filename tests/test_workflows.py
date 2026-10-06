from pathlib import Path
from app.workflows.loader import WorkflowRegistry
from app.engine.executor import WorkflowExecutor

ROOT=Path(__file__).resolve().parents[1]
registry=WorkflowRegistry(ROOT/"config/workflows.json")
executor=WorkflowExecutor()

def run(wid,data):
    return executor.execute(registry.get(wid),registry.get(wid)["trigger"],data)

def test_all_workflows_exist():
    assert len(registry.all())==10

def test_wf001():
    r=run("WF001",{"inventory_path":str(ROOT/"data/inventory.csv")})
    assert r.status=="SUCCESS" and len(r.result)==2

def test_wf002():
    r=run("WF002",{"product_path":str(ROOT/"data/products.csv"),"vendor_path":str(ROOT/"data/vendor_prices.csv")})
    assert r.status=="SUCCESS" and any(x["exception"] for x in r.result)

def test_wf003():
    r=run("WF003",{"file_path":str(ROOT/"data/vendor_products.csv")})
    assert len(r.result["invalid_rows"])==2

def test_wf004_missing_data():
    r=run("WF004",{"product":{"product_name":"Desk Lamp"}})
    assert r.result["missing_attributes"]

def test_wf005_missing_order():
    r=run("WF005",{"orders_path":str(ROOT/"data/orders.csv"),"order_id":"ORD-9999"})
    assert r.status=="NEEDS_INPUT"

def test_wf006():
    r=run("WF006",{"catalog_path":str(ROOT/"data/catalog.csv")})
    assert r.result

def test_wf007_missing_required():
    r=run("WF007",{"goal":"","dates":""})
    assert r.status=="NEEDS_INPUT"

def test_wf008():
    r=run("WF008",{"keywords":["buy shoes","how to choose shoes","buy shoes"]})
    assert len(r.result)==2

def test_wf009():
    r=run("WF009",{"employees_path":str(ROOT/"data/employees.csv"),"task":"API work","required_skills":["python","api"]})
    assert r.result["status"]=="ASSIGNED"

def test_wf010():
    r=run("WF010",{"logs_path":str(ROOT/"data/execution_logs.csv")})
    assert len(r.result)==10
