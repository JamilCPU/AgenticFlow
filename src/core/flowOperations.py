from __future__ import annotations

from typing import List, Optional

from .models import Agent, Connection, Flow


def createFlow(flowId: str, name: Optional[str] = None) -> Flow:
    return Flow(id=flowId, name=name or "")


def createAgent(
    agentId: str,
    name: Optional[str] = None,
    systemInstructions: Optional[str] = None,
    x: float = 0.0,
    y: float = 0.0,
) -> Agent:
    return Agent(
        id=agentId,
        name=name or "Agent",
        systemInstructions=systemInstructions or "",
        x=x,
        y=y,
    )


def createConnection(connectionId: str, sourceId: str, targetId: str) -> Connection:
    return Connection(id=connectionId, sourceId=sourceId, targetId=targetId)


def addAgentToFlow(flow: Flow, agent: Agent) -> None:
    if getAgentById(flow, agent.id) is not None:
        raise ValueError(f"Agent with id '{agent.id}' already exists")
    flow.agents.append(agent)


def removeAgentFromFlow(flow: Flow, agentId: str) -> None:
    flow.agents = [agent for agent in flow.agents if agent.id != agentId]
    flow.connections = [
        connection
        for connection in flow.connections
        if connection.sourceId != agentId and connection.targetId != agentId
    ]


def addConnectionToFlow(flow: Flow, connection: Connection) -> None:
    if hasDuplicateConnection(flow, connection.sourceId, connection.targetId):
        raise ValueError(
            "Connection with the same source and target already exists"
        )
    flow.connections.append(connection)


def removeConnectionFromFlow(flow: Flow, connectionId: str) -> None:
    flow.connections = [
        connection
        for connection in flow.connections
        if connection.id != connectionId
    ]


def updateConnectionTarget(
    flow: Flow,
    connectionId: str,
    targetId: str,
) -> Optional[Connection]:
    for connection in flow.connections:
        if connection.id == connectionId:
            if hasDuplicateConnection(
                flow,
                connection.sourceId,
                targetId,
                excludedId=connectionId,
            ):
                raise ValueError(
                    "Connection with the same source and target already exists"
                )
            connection.targetId = targetId
            return connection
    return None


def updateAgentInstructions(
    flow: Flow,
    agentId: str,
    instructions: str,
) -> Optional[Agent]:
    agent = getAgentById(flow, agentId)
    if agent is None:
        return None
    agent.systemInstructions = instructions
    return agent


def updateAgentPosition(
    flow: Flow,
    agentId: str,
    x: float,
    y: float,
) -> Optional[Agent]:
    agent = getAgentById(flow, agentId)
    if agent is None:
        return None
    agent.x = x
    agent.y = y
    return agent


def getAgentById(flow: Flow, agentId: str) -> Optional[Agent]:
    for agent in flow.agents:
        if agent.id == agentId:
            return agent
    return None


def getDownstreamConnections(flow: Flow, agentId: str) -> List[Connection]:
    return [
        connection
        for connection in flow.connections
        if connection.sourceId == agentId
    ]


def hasDuplicateConnection(
    flow: Flow,
    sourceId: str,
    targetId: str,
    excludedId: Optional[str] = None,
) -> bool:
    for connection in flow.connections:
        if (
            connection.sourceId == sourceId
            and connection.targetId == targetId
            and connection.id != excludedId
        ):
            return True
    return False
