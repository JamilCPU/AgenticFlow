import pytest

from src.core.flowOperations import (
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
from src.core.models import Agent, Connection, Flow


def testModelConstructionDefaultsAndTypes() -> None:
    agent = Agent(id="agent-1")
    assert agent.name == "Agent"
    assert agent.systemInstructions == ""
    assert agent.x == 0.0
    assert agent.y == 0.0
    assert isinstance(agent.name, str)
    assert isinstance(agent.systemInstructions, str)
    assert isinstance(agent.x, float)
    assert isinstance(agent.y, float)

    connection = Connection(id="conn-1", sourceId="agent-1", targetId="agent-2")
    assert connection.sourceId == "agent-1"
    assert connection.targetId == "agent-2"
    assert isinstance(connection.id, str)
    assert isinstance(connection.sourceId, str)
    assert isinstance(connection.targetId, str)

    flow = Flow(id="flow-1")
    assert flow.name == ""
    assert flow.agents == []
    assert flow.connections == []
    assert isinstance(flow.agents, list)
    assert isinstance(flow.connections, list)


def testCreateFlowProducesEmptyFlow() -> None:
    flow = createFlow("flow-1")
    assert flow.id == "flow-1"
    assert flow.name == ""
    assert flow.agents == []
    assert flow.connections == []


def testCreateAgentAddAgentToFlow() -> None:
    flow = createFlow("flow-1")
    agent = createAgent("agent-1")
    addAgentToFlow(flow, agent)
    fetchedAgent = getAgentById(flow, "agent-1")
    assert fetchedAgent is agent


def testRemoveAgentFromFlowRemovesConnections() -> None:
    flow = createFlow("flow-1")
    sourceAgent = createAgent("agent-1")
    targetAgent = createAgent("agent-2")
    otherAgent = createAgent("agent-3")
    addAgentToFlow(flow, sourceAgent)
    addAgentToFlow(flow, targetAgent)
    addAgentToFlow(flow, otherAgent)
    connectionSource = createConnection("conn-1", "agent-1", "agent-2")
    connectionTarget = createConnection("conn-2", "agent-3", "agent-2")
    addConnectionToFlow(flow, connectionSource)
    addConnectionToFlow(flow, connectionTarget)

    removeAgentFromFlow(flow, "agent-2")

    assert getAgentById(flow, "agent-2") is None
    assert getAgentById(flow, "agent-1") is not None
    assert getAgentById(flow, "agent-3") is not None
    assert flow.connections == []


def testCreateConnectionAddRemoveConnection() -> None:
    flow = createFlow("flow-1")
    connection = createConnection("conn-1", "agent-1", "agent-2")
    addConnectionToFlow(flow, connection)
    assert flow.connections == [connection]

    removeConnectionFromFlow(flow, "conn-1")
    assert flow.connections == []


def testUpdateConnectionTarget() -> None:
    flow = createFlow("flow-1")
    connection = createConnection("conn-1", "agent-1", "agent-2")
    addConnectionToFlow(flow, connection)

    updatedConnection = updateConnectionTarget(flow, "conn-1", "agent-3")
    assert updatedConnection is connection
    assert connection.targetId == "agent-3"


def testUpdateAgentInstructions() -> None:
    flow = createFlow("flow-1")
    agent = createAgent("agent-1")
    addAgentToFlow(flow, agent)

    updatedAgent = updateAgentInstructions(flow, "agent-1", "New instructions")
    assert updatedAgent is agent
    assert agent.systemInstructions == "New instructions"


def testUpdateAgentPosition() -> None:
    flow = createFlow("flow-1")
    agent = createAgent("agent-1")
    addAgentToFlow(flow, agent)

    updatedAgent = updateAgentPosition(flow, "agent-1", 12.5, -7.25)
    assert updatedAgent is agent
    assert agent.x == 12.5
    assert agent.y == -7.25


def testGetAgentByIdReturnsNoneWhenMissing() -> None:
    flow = createFlow("flow-1")
    assert getAgentById(flow, "missing") is None


def testGetDownstreamConnectionsReturnsAllOutgoing() -> None:
    flow = createFlow("flow-1")
    connectionOne = createConnection("conn-1", "agent-1", "agent-2")
    connectionTwo = createConnection("conn-2", "agent-1", "agent-3")
    connectionOther = createConnection("conn-3", "agent-2", "agent-3")
    addConnectionToFlow(flow, connectionOne)
    addConnectionToFlow(flow, connectionTwo)
    addConnectionToFlow(flow, connectionOther)

    downstream = getDownstreamConnections(flow, "agent-1")
    assert downstream == [connectionOne, connectionTwo]


def testNoDuplicateConnectionPairs() -> None:
    flow = createFlow("flow-1")
    connectionOne = createConnection("conn-1", "agent-1", "agent-2")
    connectionTwo = createConnection("conn-2", "agent-1", "agent-2")
    addConnectionToFlow(flow, connectionOne)

    with pytest.raises(ValueError):
        addConnectionToFlow(flow, connectionTwo)

    assert flow.connections == [connectionOne]
