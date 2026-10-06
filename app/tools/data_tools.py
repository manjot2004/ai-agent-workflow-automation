from pathlib import Path
import pandas as pd
from rapidfuzz.fuzz import ratio

def read_table(path):
    p = Path(path)
    return pd.read_excel(p) if p.suffix.lower() in {".xlsx", ".xls"} else pd.read_csv(p)

def inventory_restock(path, threshold=None):
    df = read_table(path)
    if threshold is None:
        threshold = df["minimum_stock"]
    else:
        threshold = float(threshold)
    df["needs_restock"] = df["current_stock"] < threshold
    df["suggested_reorder"] = (df["minimum_stock"] - df["current_stock"]).clip(lower=0)
    return df[df["needs_restock"]].to_dict("records")

def price_validation(product_path, vendor_path, limit=0.10):
    p = read_table(product_path)
    v = read_table(vendor_path)
    m = p.merge(v, on="sku", suffixes=("_internal", "_vendor"))
    m["difference_pct"] = ((m["price_vendor"] - m["price"]).abs() / m["price"]).fillna(0)
    m["exception"] = m["difference_pct"] > limit
    return m.to_dict("records")

def vendor_process(path):
    df = read_table(path)
    original = list(df.columns)
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    required = {"sku", "product_name"}
    missing_cols = sorted(required - set(df.columns))
    if missing_cols:
        return {"valid": False, "missing_columns": missing_cols, "cleaned": [], "invalid_rows": []}
    invalid = df[df["sku"].isna() | df["product_name"].isna()]
    clean = df.dropna(subset=["sku", "product_name"])
    return {"valid": len(invalid) == 0, "original_columns": original,
            "normalized_columns": list(df.columns), "cleaned": clean.to_dict("records"),
            "invalid_rows": invalid.reset_index().to_dict("records")}

def order_lookup(path, order_id=None, email=None):
    df = read_table(path)
    if order_id:
        r = df[df["order_id"].astype(str).str.lower() == str(order_id).lower()]
    elif email:
        r = df[df["customer_email"].astype(str).str.lower() == str(email).lower()]
    else:
        return None
    return None if r.empty else r.iloc[0].to_dict()

def duplicate_products(path, similarity_threshold=88):
    df = read_table(path).fillna("")
    groups, used = [], set()
    for i, a in df.iterrows():
        if i in used: continue
        group = [a.to_dict()]
        for j, b in df.iterrows():
            if j <= i or j in used: continue
            exact_sku = str(a.get("sku","")).strip() and str(a.get("sku","")).strip().lower() == str(b.get("sku","")).strip().lower()
            name_score = ratio(str(a.get("product_name","")), str(b.get("product_name","")))
            attr_score = ratio(str(a.get("attributes","")), str(b.get("attributes","")))
            score = 100 if exact_sku else round((name_score + attr_score) / 2)
            if score >= similarity_threshold:
                group.append(b.to_dict()); used.add(j)
        if len(group) > 1:
            groups.append({"confidence": "definite" if len(group) > 1 and any(str(x.get("sku","")).strip() for x in group) else "possible", "products": group})
            used.add(i)
    return groups

def assign_employee(path, task, required_skills=None, priority="normal"):
    df = read_table(path).fillna("")
    required_skills = {s.strip().lower() for s in (required_skills or []) if s.strip()}
    candidates = []
    for _, r in df.iterrows():
        skills = {s.strip().lower() for s in str(r.get("skills","")).split(",") if s.strip()}
        workload = float(r.get("workload", 0) or 0)
        capacity = float(r.get("capacity", 100) or 100)
        matched = len(required_skills & skills)
        candidates.append((matched, -(workload/capacity if capacity else 999), r.to_dict()))
    candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)
    if not candidates or candidates[0][0] < len(required_skills):
        return {"status":"ESCALATE", "reason":"No employee satisfies all required skills.", "candidates":[x[2] for x in candidates]}
    return {"status":"ASSIGNED", "employee":candidates[0][2], "matched_skills":candidates[0][0], "priority":priority}

def performance_report(path, slow_threshold=5.0):
    df = read_table(path)
    out = []
    for wid, g in df.groupby("workflow_id"):
        total=len(g); failures=(g["status"].astype(str).str.lower() != "success").sum()
        failure_rate=failures/total if total else 0
        avg_time=float(g["execution_time_sec"].mean()) if total else 0
        flagged = failure_rate > .10 or avg_time > slow_threshold
        out.append({"workflow_id":wid,"runs":total,"failure_rate":round(failure_rate,3),
                    "avg_execution_time_sec":round(avg_time,2),"flagged":flagged})
    return sorted(out, key=lambda x:(x["failure_rate"],x["avg_execution_time_sec"]), reverse=True)
