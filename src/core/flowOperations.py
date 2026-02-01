from __future__ import annotations

import uuid
from typing import List, Optional

from .models import Agent, Connection, Flow


def createId() -> str:
    return str(uuid.uuid4())


def createFlow(name: Optional[str] = None, flowId: Optional[str] = None) -> Flow:
    resolvedId = flowId or createId()
    return Flow(id=resolvedId, name=name, agents=[], connections=[])


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


def getAgentById(flow: Flow, agentId: str) -> Optional[Agent]:
    for existingAgent in flow.agents:
        if existingAgent.id == agentId:
            return existingAgent
    return None


def getDownstreamConnections(flow: Flow, sourceAgentId: str) -> List[Connection]:
    requireAgentById(flow, sourceAgentId)
    return [
        existingConnection
        for existingConnection in flow.connections
        if existingConnection.sourceId == sourceAgentId
    ]


def addAgentToFlow(flow: Flow, agent: Agent) -> Flow:
    if getAgentById(flow, agent.id) is not None:
        raise ValueError(f"Agent already exists in flow: {agent.id}")
    flow.agents.append(agent)
    return flow


def removeAgentFromFlow(flow: Flow, agentId: str) -> Flow:
    existingAgent = getAgentById(flow, agentId)
    if existingAgent is None:
        raise ValueError(f"Agent not found in flow: {agentId}")
    flow.agents = [
        remainingAgent for remainingAgent in flow.agents if remainingAgent.id != agentId
    ]
    flow.connections = [
        remainingConnection
        for remainingConnection in flow.connections
        if remainingConnection.sourceId != agentId
        and remainingConnection.targetId != agentId
    ]
    return flow


def addConnectionToFlow(flow: Flow, connection: Connection) -> Flow:
    requireAgentById(flow, connection.sourceId)
    requireAgentById(flow, connection.targetId)
    if getConnectionById(flow, connection.id) is not None:
        raise ValueError(f"Connection already exists in flow: {connection.id}")
    existingConnection = findConnectionByEndpoints(
        flow=flow,
        sourceId=connection.sourceId,
        targetId=connection.targetId,
        ignoreConnectionId=None,
    )
    if existingConnection is not None:
        raise ValueError(
            "Duplicate connection between source and target: "
            f"{connection.sourceId} -> {connection.targetId}"
        )
    flow.connections.append(connection)
    return flow


def removeConnectionFromFlow(flow: Flow, connectionId: str) -> Flow:
    existingConnection = getConnectionById(flow, connectionId)
    if existingConnection is None:
        raise ValueError(f"Connection not found in flow: {connectionId}")
    flow.connections = [
        remainingConnection
        for remainingConnection in flow.connections
        if remainingConnection.id != connectionId
    ]
    return flow


def updateConnectionTarget(
    flow: Flow,
    connectionId: str,
    newTargetId: str,
) -> Flow:
    existingConnection = requireConnectionById(flow, connectionId)
    requireAgentById(flow, newTargetId)
    if existingConnection.targetId == newTargetId:
        return flow
    duplicateConnection = findConnectionByEndpoints(
        flow=flow,
        sourceId=existingConnection.sourceId,
        targetId=newTargetId,
        ignoreConnectionId=connectionId,
    )
    if duplicateConnection is not None:
        raise ValueError(
            "Duplicate connection between source and target: "
            f"{existingConnection.sourceId} -> {newTargetId}"
        )
    existingConnection.targetId = newTargetId
    return flow


def updateAgentInstructions(
    flow: Flow,
    agentId: str,
    systemInstructions: str,
) -> Flow:
    existingAgent = requireAgentById(flow, agentId)
    existingAgent.systemInstructions = systemInstructions
    return flow


def updateAgentPosition(
    flow: Flow,
    agentId: str,
    x: float,
    y: float,
) -> Flow:
    existingAgent = requireAgentById(flow, agentId)
    existingAgent.x = x
    existingAgent.y = y
    return flow


def getConnectionById(flow: Flow, connectionId: str) -> Optional[Connection]:
    for existingConnection in flow.connections:
        if existingConnection.id == connectionId:
            return existingConnection
    return None


def requireAgentById(flow: Flow, agentId: str) -> Agent:
    existingAgent = getAgentById(flow, agentId)
    if existingAgent is None:
        raise ValueError(f"Agent not found in flow: {agentId}")
    return existingAgent


def requireConnectionById(flow: Flow, connectionId: str) -> Connection:
    existingConnection = getConnectionById(flow, connectionId)
    if existingConnection is None:
        raise ValueError(f"Connection not found in flow: {connectionId}")
    return existingConnection


def findConnectionByEndpoints(
    flow: Flow,
    sourceId: str,
    targetId: str,
    ignoreConnectionId: Optional[str],
) -> Optional[Connection]:
    for existingConnection in flow.connections:
        if (
            existingConnection.sourceId == sourceId
            and existingConnection.targetId == targetId
            and existingConnection.id != ignoreConnectionId
        ):
            return existingConnection
    return None
