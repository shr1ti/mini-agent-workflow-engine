from fastapi import FastAPI, HTTPException

from app.engine.engine import WorkflowEngine
from app.engine.models import (
    GraphConfig,
    GraphRunRequest,
    GraphRunResult,
)
from app.workflows.code_review import build_code_review_graph

app = FastAPI(title="Mini Agent Workflow Engine")

# Single global engine instance
engine = WorkflowEngine()


# -------- Startup: register the example code review graph --------

@app.on_event("startup")
def startup_event() -> None:
    build_code_review_graph(engine)


# -------- Basic health endpoint --------

@app.get("/")
def root():
    return {"message": "Mini Agent Workflow Engine is running 🚀"}


# -------- Graph APIs --------

@app.post("/graph/create")
def create_graph(graph: GraphConfig):
    """Create or overwrite a graph definition."""
    graph_id = engine.register_graph(graph)
    return {"graph_id": graph_id}


@app.post("/graph/run", response_model=GraphRunResult)
def run_graph(request: GraphRunRequest):
    try:
        result = engine.run(request)
        return result
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/graph/state/{run_id}", response_model=GraphRunResult)
def get_run_state(run_id: str):
    try:
        return engine.get_run(run_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
