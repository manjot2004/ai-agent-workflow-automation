import os, json

def generate_product_content(product: dict):
    """Offline-safe content generator. If an LLM provider is added, replace this implementation."""
    required = ["product_name", "category", "attributes", "material", "color", "target_audience"]
    missing = [k for k in required if not product.get(k)]
    name = product.get("product_name", "Product")
    category = product.get("category", "product")
    missing_note = f" Missing information: {', '.join(missing)}." if missing else ""
    desc = f"{name} is a {category} designed for {product.get('target_audience','the intended audience')}.{missing_note}"
    return {"description": desc, "short_description": desc[:150],
            "seo_title": f"{name} | {category}", "meta_description": desc[:155],
            "missing_attributes": missing}

def classify_keyword(keyword: str):
    k=keyword.lower()
    if any(x in k for x in ["how", "what", "guide", "tips"]): intent="informational"
    elif any(x in k for x in ["buy", "price", "order", "deal"]): intent="transactional"
    elif any(x in k for x in ["best", "review", "compare"]): intent="commercial"
    else: intent="navigational"
    priority="high" if intent in {"transactional","commercial"} else "medium"
    page="product page" if intent=="transactional" else ("category page" if intent=="commercial" else "blog/guide")
    return {"keyword":keyword,"intent":intent,"priority":priority,"recommended_page":page}
