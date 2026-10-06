from .models import WorkflowContext, ExecutionResult
from app.tools.data_tools import *
from app.tools.llm_tools import generate_product_content, classify_keyword

class WorkflowExecutor:
    def execute(self, workflow, request, data):
        ctx=WorkflowContext(request, data)
        wid=workflow["id"]
        try:
            if wid=="WF001":
                ctx.log("Load inventory")
                result=inventory_restock(data["inventory_path"], data.get("threshold"))
                ctx.log("Compare current stock with minimum threshold")
                ctx.log("Identify low-stock products")
                ctx.log("Calculate reorder quantity")
                ctx.log("Generate restock list")
            elif wid=="WF002":
                ctx.log("Load product and vendor prices")
                result=price_validation(data["product_path"], data["vendor_path"], data.get("limit",.10))
                ctx.log("Match products by SKU")
                ctx.log("Calculate percentage differences")
                ctx.log("Flag exceptions above 10%")
            elif wid=="WF003":
                ctx.log("Read vendor file")
                result=vendor_process(data["file_path"])
                ctx.log("Normalize column names")
                ctx.log("Validate required fields")
                ctx.log("Identify invalid rows", detail=str(len(result.get("invalid_rows",[]))))
                ctx.log("Produce cleaned dataset")
            elif wid=="WF004":
                ctx.log("Validate product attributes")
                result=generate_product_content(data["product"])
                ctx.log("Generate product description")
                ctx.log("Generate short description")
                ctx.log("Generate SEO title")
                ctx.log("Generate meta description")
            elif wid=="WF005":
                ctx.log("Validate identifier")
                result=order_lookup(data["orders_path"], data.get("order_id"), data.get("email"))
                if result is None:
                    ctx.log("Search order data","error","Order not found")
                    return ExecutionResult(wid,workflow["name"],1,"NEEDS_INPUT",ctx.trace,
                                            "No order found. Please provide another order ID or customer email.",
                                            "Order not found")
                ctx.log("Retrieve order status")
                ctx.log("Retrieve shipment information")
                ctx.log("Summarize current status")
            elif wid=="WF006":
                ctx.log("Load product catalog")
                result=duplicate_products(data["catalog_path"])
                ctx.log("Normalize identifiers")
                ctx.log("Compare product attributes")
                ctx.log("Group likely duplicates")
                ctx.log("Assign confidence")
            elif wid=="WF007":
                if not data.get("goal") or not data.get("dates"):
                    return ExecutionResult(wid,workflow["name"],1,"NEEDS_INPUT",ctx.trace,
                        "Please provide the campaign goal and dates before I generate the brief.",
                        "Missing campaign goal or dates")
                ctx.log("Validate campaign inputs")
                result={"objective":data["goal"],"audience":data.get("audience","Not specified"),
                        "products":data.get("products",[]),"promotion":data.get("promotion","Not specified"),
                        "dates":data["dates"],"messaging":f"Campaign messaging for {data['goal']}",
                        "channels":["Email","Social","Website"],"checklist":["Finalize creative","Schedule channels","Track KPIs"]}
                for s in ["Summarize products","Create messaging","Create channel recommendations","Create campaign checklist"]: ctx.log(s)
            elif wid=="WF008":
                ctx.log("Read keyword list")
                kws=list(dict.fromkeys(data["keywords"]))
                result=[classify_keyword(k) for k in kws]
                ctx.log("Remove duplicates")
                ctx.log("Classify search intent")
                ctx.log("Map keywords to recommended pages")
                ctx.log("Identify high-priority keywords")
            elif wid=="WF009":
                ctx.log("Understand task requirements")
                result=assign_employee(data["employees_path"],data["task"],data.get("required_skills"),data.get("priority","normal"))
                ctx.log("Compare employee skills")
                ctx.log("Check current workload")
                ctx.log("Rank candidates")
                ctx.log("Select employee or escalate")
            elif wid=="WF010":
                ctx.log("Load execution logs")
                result=performance_report(data["logs_path"],data.get("slow_threshold",5.0))
                ctx.log("Calculate success/failure rates")
                ctx.log("Calculate average execution time")
                ctx.log("Identify frequent errors")
                ctx.log("Identify slow workflows")
                ctx.log("Generate recommendations")
                for r in result:
                    if r["flagged"]: r["recommendation"]="Investigate failures and/or optimize slow steps."
            else:
                raise ValueError(f"Unsupported workflow {wid}")
            return ExecutionResult(wid,workflow["name"],1,"SUCCESS",ctx.trace,result)
        except Exception as e:
            ctx.log("Execution","error",str(e))
            return ExecutionResult(wid,workflow["name"],1,"FAILED",ctx.trace,None,str(e))
