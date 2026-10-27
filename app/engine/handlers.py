
from app.tools.data_tools import (
    inventory_restock,
    price_validation,
    vendor_process,
    order_lookup,
    duplicate_products,
    assign_employee,
    performance_report,
)
from app.tools.llm_tools import generate_product_content, classify_keyword


def wf001(data, ctx):
    ctx.log("Load inventory")
    result = inventory_restock(
        data["inventory_path"], data.get("threshold")
    )
    ctx.log("Compare current stock with minimum threshold")
    ctx.log("Identify low-stock products")
    ctx.log("Calculate reorder quantity")
    ctx.log("Generate restock list")
    return result


def wf002(data, ctx):
    ctx.log("Load product and vendor prices")
    result = price_validation(
        data["product_path"],
        data["vendor_path"],
        data.get("limit", 0.10),
    )
    ctx.log("Match products by SKU")
    ctx.log("Calculate percentage differences")
    ctx.log("Flag exceptions above configured limit")
    return result


def wf003(data, ctx):
    ctx.log("Read vendor file")
    result = vendor_process(data["file_path"])
    ctx.log("Normalize column names")
    ctx.log("Validate required fields")
    ctx.log(
        "Identify invalid rows",
        detail=str(len(result.get("invalid_rows", []))),
    )
    ctx.log("Produce cleaned dataset")
    return result


def wf004(data, ctx):
    ctx.log("Validate product attributes")
    result = generate_product_content(data["product"])
    ctx.log("Generate product description")
    ctx.log("Generate short description")
    ctx.log("Generate SEO title")
    ctx.log("Generate meta description")
    return result


def wf005(data, ctx):
    ctx.log("Validate identifier")
    result = order_lookup(
        data["orders_path"], data.get("order_id"), data.get("email")
    )
    if result is None:
        ctx.log("Search order data", "error", "Order not found")
        raise ValueError(
            "No order found. Please provide another order ID or customer email."
        )
    ctx.log("Retrieve order status")
    ctx.log("Retrieve shipment information")
    ctx.log("Summarize current status")
    return result


def wf006(data, ctx):
    ctx.log("Load product catalog")
    result = duplicate_products(data["catalog_path"])
    ctx.log("Normalize identifiers")
    ctx.log("Compare product attributes")
    ctx.log("Group likely duplicates")
    ctx.log("Assign confidence")
    return result


def wf007(data, ctx):
    if not data.get("goal") or not data.get("dates"):
        raise ValueError(
            "Please provide the campaign goal and dates."
        )

    ctx.log("Validate campaign inputs")
    result = {
        "objective": data["goal"],
        "audience": data.get("audience", "Not specified"),
        "products": data.get("products", []),
        "promotion": data.get("promotion", "Not specified"),
        "dates": data["dates"],
        "messaging": f"Campaign messaging for {data['goal']}",
        "channels": ["Email", "Social", "Website"],
        "checklist": [
            "Finalize creative",
            "Schedule channels",
            "Track KPIs",
        ],
    }

    for step in [
        "Summarize products",
        "Create messaging",
        "Create channel recommendations",
        "Create campaign checklist",
    ]:
        ctx.log(step)

    return result


def wf008(data, ctx):
    ctx.log("Read keyword list")
    keywords = list(dict.fromkeys(data["keywords"]))
    result = [classify_keyword(keyword) for keyword in keywords]
    ctx.log("Remove duplicates")
    ctx.log("Classify search intent")
    ctx.log("Map keywords to recommended pages")
    ctx.log("Identify high-priority keywords")
    return result


def wf009(data, ctx):
    ctx.log("Understand task requirements")
    result = assign_employee(
        data["employees_path"],
        data["task"],
        data.get("required_skills"),
        data.get("priority", "normal"),
    )
    ctx.log("Compare employee skills")
    ctx.log("Check current workload")
    ctx.log("Rank candidates")
    ctx.log("Select employee or escalate")
    return result


def wf010(data, ctx):
    ctx.log("Load execution logs")
    result = performance_report(
        data["logs_path"], data.get("slow_threshold", 5.0)
    )
    ctx.log("Calculate success/failure rates")
    ctx.log("Calculate average execution time")
    ctx.log("Identify frequent errors")
    ctx.log("Identify slow workflows")
    ctx.log("Generate recommendations")

    for row in result:
        if row["flagged"]:
            row["recommendation"] = (
                "Investigate failures and/or optimize slow steps."
            )

    return result


HANDLERS = {
    "WF001": wf001,
    "WF002": wf002,
    "WF003": wf003,
    "WF004": wf004,
    "WF005": wf005,
    "WF006": wf006,
    "WF007": wf007,
    "WF008": wf008,
    "WF009": wf009,
    "WF010": wf010,
}
