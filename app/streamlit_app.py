import os, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))

import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from app.workflows.loader import WorkflowRegistry
from app.agent.agent import WorkflowAgent
from app.llm.client import LLMClient

ROOT=Path(__file__).resolve().parents[1]
registry=WorkflowRegistry(ROOT/"config/workflows.json")
llm=LLMClient()
agent=WorkflowAgent(registry,llm if llm.enabled else None)

st.set_page_config(page_title="AI Workflow Agent", page_icon="🤖", layout="wide")
st.title("🤖 AI Agent Workflow Automation")
st.caption("Reusable, configuration-driven workflow execution — 10 business workflows, one agent architecture.")

with st.sidebar:
    st.header("System")
    st.success("LLM enabled" if llm.enabled else "Offline demo mode")
    st.metric("Available workflows",len(registry.all()))
    st.markdown("**Architecture**")
    st.code("Request → Router → Workflow Registry → Executor → Tools/Rules → Trace → Result")

examples={
"WF001":"Which products need restocking?",
"WF002":"Find products where vendor price differs by more than 10%.",
"WF003":"Process this vendor file and show invalid rows.",
"WF004":"Generate SEO content for this product.",
"WF005":"Where is order ORD-1001?",
"WF006":"Find duplicate products in the catalog.",
"WF007":"Create a campaign brief for the new collection.",
"WF008":"Classify these SEO keywords.",
"WF009":"Assign this API task to the best available developer.",
"WF010":"Which workflows are failing most often?"
}
demo_data={
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

col1,col2=st.columns([3,1])
with col1:
    request=st.text_input("User request",value="Which products need restocking?")
with col2:
    forced=st.selectbox("Workflow",["Auto"]+[w["id"]+" — "+w["name"] for w in registry.all()])

if st.button("▶ Run Agent",type="primary",use_container_width=True):
    if forced=="Auto":
        w,confidence=agent.router.route(request)
    else:
        wid=forced.split(" — ")[0]
        w=registry.get(wid); confidence=1.0
    result=agent.executor.execute(w,request,demo_data[w["id"]])
    result.selected_confidence=confidence

    st.divider()
    a,b,c=st.columns(3)
    a.metric("Selected workflow",result.workflow_id)
    b.metric("Confidence",f"{result.selected_confidence:.0%}")
    c.metric("Status",result.status)

    st.subheader(f"Selected Workflow: {result.workflow_name}")
    st.write(request)

    st.subheader("Execution Trace")
    for i,step in enumerate(result.steps,1):
        icon="✅" if step["status"]=="success" else "❌"
        st.write(f"{icon} **{i}. {step['step']}** — {step.get('detail','')}")

    st.subheader("Final Result")
    st.json(result.result) if isinstance(result.result,(dict,list)) else st.info(str(result.result))

with st.expander("Try an example"):
    for wid,text in examples.items():
        st.code(f"{wid}: {text}")
