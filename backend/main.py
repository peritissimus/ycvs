from collections import defaultdict, deque
from typing import Any, Dict, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


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


class Graph:
    def __init__(self, nodes, edges):
        self.nodes = set(nodes)
        self.edges = edges
        self.graph = defaultdict(list)
        for from_node, to_node in edges:
            self.graph[from_node].append(to_node)

    def is_connected(self):
        if not self.nodes:
            return True

        neighbor_map = defaultdict(list)
        for from_node, to_node in self.edges:
            neighbor_map[from_node].append(to_node)
            neighbor_map[to_node].append(from_node)

        start_node = list(self.nodes)[0]
        visited = set()
        queue = deque([start_node])

        while queue:
            node = queue.popleft()
            visited.add(node)
            for neighbor in neighbor_map[node]:
                if neighbor not in visited:
                    queue.append(neighbor)

        return visited == self.nodes

    def has_cycle(self):
        visited = set()
        rec_stack = set()

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in self.graph[node]:
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in self.nodes:
            if node not in visited:
                if dfs(node):
                    return True
        return False

    def is_valid_dag(self):
        return self.is_connected() and not self.has_cycle()


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
        edges = [(edge.source, edge.target) for edge in pipeline.edges]
        nodes = [node.id for node in pipeline.nodes]

        graph = Graph(nodes=nodes, edges=edges)

        return {
            "is_dag": graph.is_valid_dag(),
            "num_nodes": len(pipeline.nodes),
            "num_edges": len(pipeline.edges),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
