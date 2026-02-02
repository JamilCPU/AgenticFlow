import uuid

from src.core import createAgent, createConnection, createFlow
from src.core.factories import createId


def testCreateIdReturnsUuidString() -> None:
    createdId = createId()

    assert createdId
    uuid.UUID(createdId)


def testCreateFlowUsesProvidedValues() -> None:
    flow = createFlow(name="My Flow", flowId="flow-1")

    assert flow.id == "flow-1"
    assert flow.name == "My Flow"
    assert flow.agents == []
    assert flow.connections == []


def testCreateAgentUsesProvidedValues() -> None:
    agent = createAgent(
        name="Agent One",
        systemInstructions="Do the thing.",
        x=1.0,
        y=2.0,
        agentId="agent-1",
    )

    assert agent.id == "agent-1"
    assert agent.name == "Agent One"
    assert agent.systemInstructions == "Do the thing."
    assert agent.x == 1.0
    assert agent.y == 2.0


def testCreateConnectionUsesProvidedValues() -> None:
    connection = createConnection(
        sourceId="agent-1",
        targetId="agent-2",
        connectionId="connection-1",
    )

    assert connection.id == "connection-1"
    assert connection.sourceId == "agent-1"
    assert connection.targetId == "agent-2"
