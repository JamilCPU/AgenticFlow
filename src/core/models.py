from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Agent:
    id: str
    name: str
    systemInstructions: str
    x: float
    y: float


@dataclass
class Connection:
    id: str
    sourceId: str
    targetId: str


@dataclass
class Flow:
    id: str
    name: Optional[str] = None
    agents: List[Agent] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
