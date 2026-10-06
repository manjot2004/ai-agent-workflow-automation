from rapidfuzz.fuzz import token_set_ratio

class WorkflowRouter:
    def __init__(self, workflows, llm=None):
        self.workflows = workflows
        self.llm = llm

    def route(self, request: str):
        if self.llm:
            try:
                decision=self.llm.classify(request,self.workflows)
                by_id={w["id"]:w for w in self.workflows}
                if decision and decision.get("workflow_id") in by_id:
                    return by_id[decision["workflow_id"]], float(decision.get("confidence",0.9))
            except Exception:
                pass

        req=request.lower()
        keywords = {
            "WF001":["restock","inventory","stock"],
            "WF002":["vendor price","price","10%","difference"],
            "WF003":["vendor file","vendor spreadsheet","invalid rows","process file"],
            "WF004":["description","seo content","product content"],
            "WF005":["order","shipment","tracking","status"],
            "WF006":["duplicate","similar product","catalog"],
            "WF007":["campaign","marketing","campaign brief"],
            "WF008":["keyword","search intent","seo keyword"],
            "WF009":["assign","employee","developer","task"],
            "WF010":["performance","workflow","failing","execution logs"],
        }
        best=None
        for w in self.workflows:
            text=" ".join([w["name"],w["trigger"]," ".join(w["inputs"]),w["decision_logic"]]).lower()
            score=token_set_ratio(req,text)/100
            hits=sum(1 for k in keywords[w["id"]] if k in req)
            score=min(1,score+.08*hits)
            if best is None or score>best[1]: best=(w,score)
        return best[0],round(best[1],3)
