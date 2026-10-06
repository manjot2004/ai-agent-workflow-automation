import json
import os

class LLMClient:
    """Optional LLM adapter. The app remains fully runnable without an API key."""

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self._client = None
        if self.api_key:
            try:
                from openai import OpenAI
                self._client = OpenAI(api_key=self.api_key)
            except Exception:
                self._client = None

    @property
    def enabled(self):
        return self._client is not None

    def classify(self, request, workflows):
        if not self.enabled:
            return None
        catalog = [{"id": w["id"], "name": w["name"], "trigger": w["trigger"]} for w in workflows]
        prompt = (
            "Select the single best workflow for the user request. "
            "Return JSON only: {\"workflow_id\":\"WFxxx\",\"confidence\":0.0,\"reason\":\"...\"}.\\n"
            f"Workflows: {json.dumps(catalog)}\\nRequest: {request}"
        )
        r = self._client.chat.completions.create(
            model=self.model,
            temperature=0,
            response_format={"type":"json_object"},
            messages=[{"role":"system","content":"You are a workflow router."},
                      {"role":"user","content":prompt}]
        )
        return json.loads(r.choices[0].message.content)

    def generate(self, system, user):
        if not self.enabled:
            return None
        r=self._client.chat.completions.create(
            model=self.model, temperature=0.4,
            messages=[{"role":"system","content":system},{"role":"user","content":user}]
        )
        return r.choices[0].message.content
