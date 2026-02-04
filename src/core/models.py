from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class Agent:
    id: str
    name: str = "Agent"
    systemInstructions: str = ""
    x: float = 0.0
    y: float = 0.0


@dataclass
class Connection:
    id: str
    sourceId: str
    targetId: str


@dataclass
class Flow:
    id: str
    name: str = ""
    agents: List[Agent] = field(default_factory=list)
    connections: List[Connection] = field(default_factory=list)
