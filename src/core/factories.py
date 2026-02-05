from __future__ import annotations

import uuid
from typing import Optional

from .models import Agent, Connection, Flow


def createId() -> str:
    return str(uuid.uuid4())


def createFlow(name: Optional[str] = None, flowId: Optional[str] = None) -> Flow:
    resolvedId = flowId or createId()
    return Flow(id=resolvedId, name=name)


def createAgent(
    name: str,
    systemInstructions: str = "",
    x: float = 0.0,
    y: float = 0.0,
    agentId: Optional[str] = None,
) -> Agent:
    resolvedId = agentId or createId()
    return Agent(
        id=resolvedId,
        name=name,
        systemInstructions=systemInstructions,
        x=x,
        y=y,
    )


def createConnection(
    sourceId: str,
    targetId: str,
    connectionId: Optional[str] = None,
) -> Connection:
    resolvedId = connectionId or createId()
    return Connection(id=resolvedId, sourceId=sourceId, targetId=targetId)
