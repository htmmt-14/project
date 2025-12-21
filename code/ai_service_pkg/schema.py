# ai_pkg/schema.py
from dataclasses import dataclass
from typing import List

@dataclass
class WorkUnit:
    id: str
    star: int
    text: str

@dataclass
class Batch:
    batch: List[WorkUnit]

@dataclass
class WorkerResult:
    id: str
    labels: List[str]

@dataclass
class ResultPayload:
    from_worker: str
    data: List[WorkerResult]
