import pytest

from src.core import (
    addAgentToFlow,
    addConnectionToFlow,
    createAgent,
    createConnection,
    createFlow,
    getAgentById,
    getDownstreamConnections,
    removeAgentFromFlow,
    removeConnectionFromFlow,
    updateAgentInstructions,
    updateAgentPosition,
    updateConnectionTarget,
)
from src.core.flowOperations import (
    findConnectionByEndpoints,
    getConnectionById,
    requireAgentById,
    requireConnectionById,
)


def testAddAgentAndLookup() -> None:
    flow = createFlow(flowId="flow-1")
    agent = createAgent(
        name="Agent One",
        systemInstructions="Do the thing.",
        x=1.0,
        y=2.0,
        agentId="agent-1",
    )
    addAgentToFlow(flow, agent)

    foundAgent = getAgentById(flow, "agent-1")
    assert foundAgent is agent


def testAddAgentDuplicateId() -> None:
    flow = createFlow(flowId="flow-1")
    agent = createAgent(name="Agent One", agentId="agent-1")
    addAgentToFlow(flow, agent)

    with pytest.raises(ValueError):
        addAgentToFlow(flow, agent)


def testAddConnectionFanOut() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgentOne = createAgent(name="Target One", agentId="agent-2")
    targetAgentTwo = createAgent(name="Target Two", agentId="agent-3")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgentOne)
    addAgentToFlow(flow, targetAgentTwo)

    connectionOne = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    connectionTwo = createConnection(
        sourceId="agent-1",
        targetId="agent-3",
        connectionId="connection-2",
    )
    addConnectionToFlow(flow, connectionOne)
    addConnectionToFlow(flow, connectionTwo)

    downstream = getDownstreamConnections(flow, "agent-1")
    downstreamIds = {connection.id for connection in downstream}
    assert downstreamIds == {"connection-1", "connection-2"}


def testAddConnectionRejectsDuplicateEndpoints() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgent = createAgent(name="Target", agentId="agent-2")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)

    connectionOne = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    connectionTwo = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-2",
    )
    addConnectionToFlow(flow, connectionOne)

    with pytest.raises(ValueError):
        addConnectionToFlow(flow, connectionTwo)


def testAddConnectionMissingAgent() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    addAgentToFlow(flow, sourceAgent)
    connection = createConnection(
        sourceId="agent-1",
        targetId="missing-agent",
        connectionId="connection-1",
    )

    with pytest.raises(ValueError):
        addConnectionToFlow(flow, connection)


def testRemoveAgentRemovesConnections() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgent = createAgent(name="Target", agentId="agent-2")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)
    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    addConnectionToFlow(flow, connection)

    removeAgentFromFlow(flow, "agent-1")

    assert getAgentById(flow, "agent-1") is None
    assert flow.connections == []
    assert getAgentById(flow, "agent-2") is targetAgent


def testRemoveConnectionFromFlow() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgent = createAgent(name="Target", agentId="agent-2")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)
    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    addConnectionToFlow(flow, connection)

    removeConnectionFromFlow(flow, "connection-1")

    assert flow.connections == []


def testUpdateAgentInstructionsAndPosition() -> None:
    flow = createFlow(flowId="flow-1")
    agent = createAgent(name="Agent One", agentId="agent-1")
    addAgentToFlow(flow, agent)

    updateAgentInstructions(flow, "agent-1", "New instructions")
    updateAgentPosition(flow, "agent-1", x=10.5, y=20.25)

    assert agent.systemInstructions == "New instructions"
    assert agent.x == 10.5
    assert agent.y == 20.25


def testUpdateConnectionTarget() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    initialTarget = createAgent(name="Target One", agentId="agent-2")
    newTarget = createAgent(name="Target Two", agentId="agent-3")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, initialTarget)
    addAgentToFlow(flow, newTarget)

    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    addConnectionToFlow(flow, connection)

    updateConnectionTarget(flow, "connection-1", "agent-3")

    assert connection.targetId == "agent-3"


def testUpdateConnectionTargetRejectsDuplicate() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgentOne = createAgent(name="Target One", agentId="agent-2")
    targetAgentTwo = createAgent(name="Target Two", agentId="agent-3")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgentOne)
    addAgentToFlow(flow, targetAgentTwo)

    connectionOne = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    connectionTwo = createConnection(
        sourceId="agent-1",
        targetId="agent-3",
        connectionId="connection-2",
    )
    addConnectionToFlow(flow, connectionOne)
    addConnectionToFlow(flow, connectionTwo)

    with pytest.raises(ValueError):
        updateConnectionTarget(flow, "connection-1", "agent-3")


def testGetDownstreamConnectionsValidatesAgent() -> None:
    flow = createFlow(flowId="flow-1")

    with pytest.raises(ValueError):
        getDownstreamConnections(flow, "missing-agent")


def testGetConnectionByIdReturnsConnection() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgent = createAgent(name="Target", agentId="agent-2")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)
    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    addConnectionToFlow(flow, connection)

    foundConnection = getConnectionById(flow, "connection-1")

    assert foundConnection is connection


def testRequireAgentByIdReturnsAgent() -> None:
    flow = createFlow(flowId="flow-1")
    agent = createAgent(name="Agent", agentId="agent-1")
    addAgentToFlow(flow, agent)

    foundAgent = requireAgentById(flow, "agent-1")

    assert foundAgent is agent


def testRequireAgentByIdMissingRaises() -> None:
    flow = createFlow(flowId="flow-1")

    with pytest.raises(ValueError):
        requireAgentById(flow, "missing-agent")


def testRequireConnectionByIdMissingRaises() -> None:
    flow = createFlow(flowId="flow-1")

    with pytest.raises(ValueError):
        requireConnectionById(flow, "missing-connection")


def testFindConnectionByEndpoints() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgent = createAgent(name="Target", agentId="agent-2")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)
    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    addConnectionToFlow(flow, connection)

    foundConnection = findConnectionByEndpoints(
        flow=flow,
        sourceId="agent-1",
        targetId="agent-2",
        ignoreConnectionId=None,
    )

    assert foundConnection is connection


def testFindConnectionByEndpointsIgnoresId() -> None:
    flow = createFlow(flowId="flow-1")
    sourceAgent = createAgent(name="Source", agentId="agent-1")
    targetAgent = createAgent(name="Target", agentId="agent-2")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)
    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )
    addConnectionToFlow(flow, connection)

    foundConnection = findConnectionByEndpoints(
        flow=flow,
        sourceId="agent-1",
        targetId="agent-2",
        ignoreConnectionId="connection-1",
    )

    assert foundConnection is None
