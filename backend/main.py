from typing import Any, Dict, List

import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# add auth
# add ratelimit
# add monitoring
# add analytics


class Node(BaseModel):
    id: str
    type: str
    data: Dict[str, Any]


class Edge(BaseModel):
    source: str
    target: str
    id: str


class Pipeline(BaseModel):
    nodes: List[Node]
    edges: List[Edge]


def create_graph(data: Pipeline):
    G = nx.DiGraph()
    G.add_nodes_from([node.id for node in data.nodes])
    G.add_edges_from([(edge.source, edge.target) for edge in data.edges])
    return G


app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Working"}


@app.post("/pipelines/parse")
def parse_pipeline(pipeline: Pipeline):
    try:
        graph = create_graph(pipeline)
        return {
            "is_dag": nx.is_weakly_connected(graph),
            "num_nodes": len(pipeline.nodes),
            "num_edges": len(pipeline.edges),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
