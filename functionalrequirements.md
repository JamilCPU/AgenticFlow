# AgenticFlow — Functional Requirements

> **Purpose:** This document is the source of truth for functional requirements. It will be updated as decisions are made and scope is clarified. Use it to drive design and implementation.

---

## 1. Product Overview

**AgenticFlow** is a platform where users can **create** and **manage** AI agents **in real time**.

- **Create:** Define, configure, and wire up AI agents (model, instructions, tools, behavior).
- **Manage:** Deploy, run, monitor, and adjust agents while they are active.
- **Real time:** Changes and agent activity are reflected live; users see and control agents as they operate.

---

## 2. Stakeholders & Users

| Role | Description |
|------|-------------|
| **End User / Agent Creator** | Primary user who creates, configures, and runs agents. |
| *(TBD)* | *Add other roles if needed (e.g., Viewer, Admin, API Consumer).* |

---

## 3. Core Concepts

| Concept | Definition |
|--------|------------|
| **Agent** | A configured AI entity with: identity (name, purpose), a backing model/API, system instructions, and an optional set of tools/capabilities. Each agent has its **own context** plus whatever context is provided to it when it runs. |
| **Real-time management** | Editing agent config, viewing runs, and controlling execution (e.g., pause, stop) with immediate effect. |
| **Flow** | A connected system of agents. The user defines how output from one agent is delivered to one or more **receiving agents**. One **trigger** causes the flow to run. |
| **Trigger** | The event that starts a flow. Initially: **(a)** user sends a message/request in the GUI to an agent, or **(b)** an agent receives output from another agent and begins working. *(Later: external sources, e.g. webhooks, API.)* |
| **Run** | A single execution of a flow: one trigger leads to one or more agents running, with outputs potentially fanning out to multiple downstream agents. |
| **Connection** | The medium that links two **agent nodes**; output flows from the source to the target. The user can add, edit, and delete connections. |
| **Agent node** | An agent as represented on the flow canvas. The user can add agent nodes to a flow and remove them from a flow. |

---

## 4. Functional Requirements

### 4.1 Application & Interface

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-1.1 | AgenticFlow is a **desktop application**. | |
| FR-1.2 | The user interacts primarily through a **GUI**; creation, configuration, and running of agents and flows happen in the interface. | |

### 4.2 Agent Creation & Context

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-2.1 | User can create an **individual agent** with its own identity and configuration. | |
| FR-2.2 | Each agent operates within **its own context** (state, history, or config as defined for that agent). | |
| FR-2.3 | When an agent runs, it also receives **context provided to it** (e.g., from the trigger: user message, or output from an upstream agent). | |
| FR-2.4 | Each agent is backed by an **LLM/model**. For the MVP, the model is **fixed to a single Claude model** (not user-selectable); support for choosing among multiple models or providers is planned for later. | |
| FR-2.5 | Before a flow run starts, the application **validates that the model is connected properly** for each agent in the flow (e.g., API reachable, credentials valid). If validation fails, the run is **blocked** and the user is informed; the run does not proceed until the connection is valid. | Pre-run check. |
| FR-2.6 | For the MVP, model/API **credentials** (e.g., Claude API key) are read from an **environment variable**; the user does not enter them in the GUI. Support for defining and storing the API key in the GUI is planned for later. | |
| FR-2.7 | User can **edit system instructions (model instructions) on a per-agent basis**; each agent has its own editable instructions that define its behavior. | |

### 4.3 Multi-Agent Flows

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-3.1 | User can define a **flow**: a system of agents where outputs are routed between agents. | |
| FR-3.2 | The output of one agent can be delivered to **multiple receiving agents**. | Fan-out. |
| FR-3.3 | **One trigger** starts the flow; from that event, the entire connected system can run (agents run as they receive their input). | |

### 4.4 Triggering a Run (Prioritized)

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-4.1 | User can **send a message or request to an agent from the GUI**. That action serves as the trigger to start a flow. | Option B — primary. |
| FR-4.2 | When an agent produces output, that output can be **delivered to one or more receiving agents**; receipt of that output acts as the trigger for those agents to begin working. | Option A — primary. |
| FR-4.3 | The application supports **both** user-in-GUI triggers and agent-output-to-agent triggers as first-class ways to start or continue a run. | |

### 4.5 Real-Time Run Visualization

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-5.1 | While a flow is running, the user sees the entire flow in the GUI. | |
| FR-5.2 | **Lines** connect agents, showing the direction of output from one agent to another. | |
| FR-5.3 | Each agent is enclosed by a **border**. | |
| FR-5.4 | When **data is in transit** on a connection (output being sent or received between agents): **only the line** (connection) **pulsates** and may change color and highlight; agent borders do not pulsate in this state. | |
| FR-5.5 | When an **agent is thinking or processing** a query: that **agent's border** **pulsates** and may change color and highlight. | |
| FR-5.6 | The user can observe which parts of the flow are working at any moment through these visual cues (transit = line; processing = agent border). | Game-like feedback. |
| FR-5.7 | When the user **hovers over an agent** (node), information about that **agent's state** is revealed (e.g., output, messages, model state). | |
| FR-5.8 | When the user **hovers over a line** (connection), information pertaining to that connection's **state** is revealed (e.g., data in transit, recent output). | |

### 4.6 Flow Definition & Editing (GUI)

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-6.1 | User can **drag** from one agent to another to **create a connection** (output flows from the source agent to the target agent). | Drag-to-connect. |
| FR-6.2 | User can **click** on an agent to **select** it. | |
| FR-6.3 | When an agent is selected, the user can **add** connections (connect this agent to another, as sender or receiver), **edit** existing connections (e.g., change target or properties), and **delete** connections. **Connections** are the mediums that link agent nodes; the user manages them separately from nodes. | |
| FR-6.4 | User can **add an agent (node) to the flow** (create and place a new agent on the flow canvas, or add an existing agent to the flow). | |
| FR-6.5 | User can **remove an agent (node) from the flow**; doing so removes that agent and its connections from the flow. | |

### 4.7 Persistence

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-7.1 | Flows and agent data are **persisted in local files**; the user can **save** the current flow (and its agents and connections) and **load** from a saved file. | |
| FR-7.2 | The application supports **loading saved data on application startup** (e.g., restore last opened file or prompt to open). | |

### 4.8 Run Controls

| ID | Requirement | Notes |
|----|-------------|-------|
| FR-8.1 | The user **must** be able to **stop a flow while it is running**; the run is aborted and does not continue. | |

---

## 5. Out of Scope (Initial Release)

| Item | Description |
|------|-------------|
| **External triggers** | Triggers from outside the app (e.g., webhooks, HTTP API, other systems) are **not** in the initial release. Support for these is planned for a later version. | Option C — deferred. |
| **User-selectable models / multiple model providers** | For MVP, a single Claude model is hardcoded. Choosing among multiple models or providers (e.g., OpenAI, Ollama) is planned for later. | |
| **GUI for defining/storing API credentials** | For MVP, credentials are read from an environment variable. A GUI to define and store the API key is planned for later. | |
| **Pause** | User can stop a run; **pause** (and resume) is not in the initial release. | |

---

## 6. Technical / Implementation

| Item | Description |
|------|-------------|
| **ADK (Python)** | The application will leverage **ADK** in **Python** for the agent runtime and logic. | |
| **Credentials (MVP)** | Model/API credentials (e.g., Claude API key) are read from an **environment variable**. | |

---
