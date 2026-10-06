# AI Agent Workflow Automation

A reusable, configuration-driven Python agent for the 10 business workflows in the supplied technical assessment.

## Architecture

User Request -> Workflow Router -> Workflow Registry -> Generic Executor -> Tools/Rules -> Execution Trace -> Final Result

The design deliberately avoids 10 hard-coded chatbots. Workflow definitions live in `config/workflows.json`, while reusable execution logic lives under `app/engine` and reusable tools under `app/tools`.

### LLM boundary

The architecture is ready for an LLM provider. The LLM should be used for ambiguous intent routing, natural-language extraction, generation, and semantic classification. Deterministic business rules (thresholds, validation, ranking, metrics) stay in Python for reliability and testability. The offline demo includes safe local fallbacks so the project can run without an API key.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

## Run tests

```bash
pytest -q
```

## Run the CLI

```bash
python -m app.main run "Which products need restocking?" --workflow WF001
```

Try each workflow with the examples in `examples/requests.md`.

## Adding workflow #11

1. Add a new workflow definition to `config/workflows.json`.
2. Add/reuse tools in `app/tools`.
3. Add the workflow-specific execution adapter in the generic executor only if its tool composition cannot be represented by existing reusable tools.
4. Add one test.

The router and registry do not require a new chatbot.

## Assessment coverage

- Workflow selection: `app/agent/router.py`
- Reusable execution: `app/engine/executor.py`
- Workflow source/config: `config/workflows.json`
- Tool abstraction: `app/tools/`
- Conditions/errors: executor status `NEEDS_INPUT` / `FAILED`
- Execution trace: every result contains selected workflow and executed steps
- All 10 workflows: implemented
- Tests: `tests/test_workflows.py`
- Sample data: `data/`

## Loom demo

Show:
1. Repository structure.
2. `config/workflows.json` as the workflow source.
3. A normal request and its selected workflow.
4. A condition/error case such as missing order.
5. A generated-content workflow.
6. `pytest -q`.
7. Explain that WF011 is added as configuration plus reusable tools rather than a new chatbot.

## Note

The supplied assessment spreadsheet is included in the repository as `data/AI_Agent_Workflow_Assessment.xlsx`.


## Demo UI

Run:

```bash
streamlit run app/streamlit_app.py
```

The UI shows:
- Natural-language request
- Auto workflow selection
- LLM/offline mode
- Selected workflow and confidence
- Every executed step
- Final result
- All 10 workflow examples

## Optional OpenAI integration

Copy `.env.example` to `.env` and set:

```text
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
```

The application automatically uses the LLM for workflow selection when configured. Without a key, it falls back to deterministic routing so evaluators can still run the project.

## Why this is scalable

A new workflow is represented as configuration plus reusable tools. The router and UI discover workflows from the registry. This avoids creating a separate chatbot/agent for each business process.
