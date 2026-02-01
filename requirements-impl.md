# AgenticFlow — Implementation Plan

> **Purpose:** This document describes the optimal implementation approach for AgenticFlow. It references [functionalrequirements.md](./functionalrequirements.md) (FRs) and translates them into structure, milestones, and technical decisions.

---

## 1. Relationship to Functional Requirements

| Document | Role |
|----------|------|
| **functionalrequirements.md** | **What** to build: product behavior, user capabilities, out-of-scope. |
| **requirements-impl.md** | **How** to build it: tech choices, sequence, design, and FR traceability. |

Implement in **vertical slices** and **milestones**, not strict FR document order. Each milestone delivers a testable slice; FRs are closed as they are satisfied.

---

## 2. Technical Stack

Aligned with **FR-1.1** (desktop), **FR-1.2** (GUI), and **Technical / Implementation** in the FR doc:

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Desktop + GUI** | **PySide6** | Single process with ADK; `QGraphicsScene` / `QGraphicsView` suit node-and-edge canvas, drag, hover, and custom painting (lines, borders, pulsating). Good for desktop on Windows, macOS, Linux. |
| **Agent runtime** | **Google's Agent Development Kit (ADK)** (Python) | Per FR doc: agent logic and model calls. Single model (see §8 for model choice); credentials from env. |
| **Persistence** | **JSON** in local files | FR-7.1, FR-7.2: simple, debuggable, works with version control. One file per flow (or one project file containing the current flow). |
| **Credentials (MVP)** | **Environment variable** | FR-2.6: e.g. `GOOGLE_API_KEY`. Read at startup and before validation (FR-2.5). The credentials flow (read from env, validate, report result) must be **completable via the UI**: the user can trigger validation and see success or failure in the GUI. |
| **Async / execution** | **asyncio** + **qasync** + **cancellation** | Run flows in an async loop integrated with Qt's event loop via **qasync**; support `stop` (FR-8.1) via `asyncio.Task.cancel` or a shared stop flag. |

**Alternative:** Tauri + web frontend (React/Svelte) for the canvas if the team prefers web UI and can manage a Python sidecar for ADK. For MVP, PySide6 keeps everything in one process.

---

## 3. Project Structure

```
AgenticFlow/
├── src/
│   ├── core/                 # Data models and flow operations
│   │   ├── models.py
│   │   ├── flowOperations.py
│   │   └── __init__.py
│   ├── persistence/          # Save/load (FR-7.1, FR-7.2)
│   │   ├── storage.py
│   │   └── __init__.py
│   ├── runtime/              # ADK, execution, validation (FR-2.4–2.5, FR-3.x, FR-4.x, FR-8.1)
│   │   ├── executor.py
│   │   ├── validation.py
│   │   ├── credentials.py
│   │   ├── context.py
│   │   ├── events.py
│   │   ├── state.py
│   │   └── __init__.py
│   └── ui/                  # Main window, canvas, panels (FR-1.2, FR-5.x, FR-6.x)
│       ├── main.py
│       ├── actions.py
│       ├── canvas/
│       │   ├── scene.py      # QGraphicsScene: nodes, edges
│       │   ├── node.py       # Agent node widget
│       │   └── edge.py       # Connection line
│       ├── panels/           # Agent editor (instructions), run input, etc.
│       └── __init__.py
├── tests/
├── functionalrequirements.md
├── requirements-impl.md
└── README.md
```

---

## 4. Data Model

Supports **FR-2.1**, **FR-2.7**, **FR-3.1**, **FR-6.x**, **FR-7.1**.

| Entity | Fields | Notes |
|--------|--------|-------|
| **Agent** | `id`, `name`, `system_instructions`, `x`, `y` | `x`, `y` for canvas position. Model fixed per FR-2.4. |
| **Connection** | `id`, `source_id`, `target_id` | Source/target are agent `id`s. FR-3.2: one source → multiple targets (fan-out). |
| **Flow** | `id`, `name?`, `agents: List[Agent]`, `connections: List[Connection]` | Root for save/load. |

**Endpoints (data + flow operations):**
- [GET] `core/models/agent`
- [GET] `core/models/connection`
- [GET] `core/models/flow`
- [POST] `core/flow-operations/create-flow`
- [POST] `core/flow-operations/create-agent`
- [POST] `core/flow-operations/create-connection`
- [POST] `core/flow-operations/add-agent-to-flow`
- [DELETE] `core/flow-operations/remove-agent-from-flow`
- [POST] `core/flow-operations/add-connection-to-flow`
- [DELETE] `core/flow-operations/remove-connection-from-flow`
- [PUT] `core/flow-operations/update-connection-target`
- [PUT] `core/flow-operations/update-agent-instructions`
- [PUT] `core/flow-operations/update-agent-position`
- [GET] `core/flow-operations/get-agent-by-id`
- [GET] `core/flow-operations/get-downstream-connections`

`Agent`’s “own context” (FR-2.2) and “context provided to it” (FR-2.3) are handled at **runtime** in the executor (per-run history and input), not in the persisted model. Persist only what defines the flow and agent config.

---

## 5. Persistence (Local Files)

**FR-7.1**, **FR-7.2**.

- **Format:** JSON. One file per flow, or one “project” file with the current flow.
- **Schema (minimal):**
  - `flow`: `{ "id", "name?", "agents": [ { "id", "name", "system_instructions", "x", "y" } ], "connections": [ { "id", "source_id", "target_id" } ] }`
- **Load on startup (FR-7.2):** Store “last opened path” (e.g. in a small app config or OS app-data). On startup: if exists, offer to open it or auto-open; else empty canvas.
- **Save/Load:** Explicit Save/Save As and Open in GUI; `persistence.storage` reads/writes JSON and returns/accepts `Flow`.

**Endpoints (persistence):**
- [PUT] `persistence/storage/save-flow`
- [GET] `persistence/storage/load-flow`
- [PUT] `persistence/storage/save-last-path`
- [GET] `persistence/storage/load-last-path`

---

## 6. Execution and Run-Time Events

**FR-3.x**, **FR-4.x**, **FR-8.1**; feeds **FR-5.x** (visualization).

### 6.1 Trigger and Routing

- **User message (FR-4.1):** User picks an **entry agent** (e.g. by selecting it and using “Run with message”) and enters text. That message is the trigger; it goes to that agent as input.
- **Agent → agent (FR-4.2, FR-4.3):** When an agent produces an output, the executor looks up `connections` with `source_id == that agent` and delivers the output to each `target_id`. Those agents run when they receive input (and can again fan out).

**Endpoints (trigger + routing):**
- [POST] `runtime/executor/run-flow`
- [GET] `core/flow-operations/get-downstream-connections`

### 6.2 Execution Model

- **Async run:** One `asyncio` task per logical “run” of the flow. Run agent A; when A finishes, schedule B, C, … for each connection. Use a shared **cancel** flag or `asyncio.Task.cancel` for **FR-8.1** (stop).
- **Pre-run validation (FR-2.5):** Before starting, for each distinct agent in the flow: check env var is set and (optionally) that the Google API (via ADK) is reachable. If any check fails: block run, show message in GUI.

**Endpoints (execution + validation):**
- [POST] `runtime/executor/run-agent`
- [POST] `runtime/executor/run-flow`
- [POST] `runtime/executor/create-cancel-token`
- [DELETE] `runtime/executor/cancel-run`
- [POST] `runtime/validation/validate-flow`
- [POST] `runtime/validation/validate-adk-connectivity`
- [GET] `runtime/credentials/get-google-api-key`
- [POST] `runtime/credentials/validate-google-api-key`
- [POST] `runtime/context/build-agent-context`
- [PUT] `runtime/context/update-agent-context`

### 6.3 Events for the GUI (FR-5.x)

Emit from the executor; GUI subscribes and updates the canvas:

| Event | Payload | GUI behavior |
|-------|---------|--------------|
| `agent_processing_started` | `agent_id` | Agent border pulsates (FR-5.5). |
| `agent_processing_finished` | `agent_id` | Border stops pulsating. |
| `data_in_transit` | `connection_id` or `(source_id, target_id)` | Line pulsates (FR-5.4); agent borders not. |
| `data_delivered` | `connection_id` | Line stops pulsating. |
| `agent_output` | `agent_id`, `output` (and any structured state) | Store for hover (FR-5.7). |
| `connection_data` | `connection_id`, `data` | Store for hover (FR-5.8). |

Implement via a small **event bus** or **callback registry** from `runtime` to `gui`.

**Endpoints (events + hover state):**
- [GET] `runtime/events/runtime-event-bus`
- [POST] `runtime/events/emit-event`
- [POST] `runtime/events/register-listener`
- [PUT] `runtime/state/set-agent-output`
- [GET] `runtime/state/get-agent-state`
- [PUT] `runtime/state/set-connection-data`
- [GET] `runtime/state/get-connection-state`

---

## 7. GUI Components

**FR-1.2**, **FR-5.x**, **FR-6.x**.

### 7.1 Main Window

- **Menu or toolbar:** New, Open, Save, Save As; Run (or “Run with message” when an entry agent is selected); **Stop** (FR-8.1) — enabled only while a run is active.
- **Central:** `QGraphicsView` + `QGraphicsScene` for the flow canvas.
- **Side panel(s):** When an agent is selected (FR-6.2): show **system instructions** editor (FR-2.7) and, if needed, add/edit/delete **connections** (FR-6.3). Or a context menu for connections.

**Endpoints (main window actions):**
- [POST] `ui/main/create-main-window`
- [POST] `ui/actions/run-selected-agent-with-message`
- [DELETE] `ui/actions/stop-active-run`
- [GET] `ui/actions/open-flow-from-path`
- [PUT] `ui/actions/save-flow-to-path`
- [GET] `ui/actions/restore-last-flow`

### 7.2 Flow Canvas (FR-5.1–5.3, FR-5.6, FR-6.x)

- **Nodes:** Custom `QGraphicsItem` or `QGraphicsRectItem` for each agent; `(x,y)` from model. **Border** around each (FR-5.3). On **click** → select (FR-6.2). On **hover** → show tooltip or popover with agent state (FR-5.7); data comes from runtime events.
- **Edges:** `QGraphicsPathItem` or custom line from `source` node to `target` node. **Hover** → tooltip with connection state (FR-5.8).

**Pulsating (FR-5.4, FR-5.5):** Use `QPropertyAnimation` on opacity/scale or a timer-driven repaint. When `agent_processing_started(agent_id)` → animate that node’s border; when `data_in_transit(connection_id)` → animate that edge only.

**Endpoints (canvas rendering + hover):**
- [POST] `ui/canvas/scene/render-flow`
- [PUT] `ui/canvas/scene/set-agent-processing-state`
- [PUT] `ui/canvas/scene/set-connection-transit-state`
- [POST] `ui/canvas/scene/show-agent-hover`
- [POST] `ui/canvas/scene/show-connection-hover`
- [PUT] `ui/actions/select-agent-by-id`

### 7.3 Drag-to-Connect (FR-6.1)

- On node: rubber-band or temporary line from node’s edge while dragging. On drop on another node: create `Connection(source_id, target_id)`, add to `Flow`, update scene. Validate: no duplicate `(source_id, target_id)`; no self-loops if not allowed.

**Endpoints (drag connect):**
- [POST] `ui/actions/start-connection-drag`
- [POST] `ui/actions/complete-connection-drag`
- [POST] `core/flow-operations/create-connection`
- [POST] `core/flow-operations/add-connection-to-flow`

### 7.4 Add/Remove Nodes and Connections (FR-6.3–6.5)

- **Add agent (FR-6.4):** e.g. “Add agent” button or double-click on canvas; create `Agent` with default `name` and `system_instructions`, append to `flow.agents`, place at click/drop position.
- **Remove agent (FR-6.5):** On delete (key or context menu) for selected agent: remove from `flow.agents` and all `connections` where `source_id` or `target_id` equals that `id`.
- **Add/edit/delete connections (FR-6.3):** When an agent is selected: list its connections; buttons or menu to add (choose target), edit (change target), delete. Alternatively, select an edge to edit/delete that connection.

**Endpoints (node + connection editing):**
- [POST] `ui/actions/add-agent-at-position`
- [DELETE] `ui/actions/remove-selected-agent`
- [PUT] `ui/actions/update-selected-agent-instructions`
- [POST] `core/flow-operations/create-agent`
- [POST] `core/flow-operations/add-agent-to-flow`
- [DELETE] `core/flow-operations/remove-agent-from-flow`
- [PUT] `core/flow-operations/update-agent-instructions`
- [PUT] `core/flow-operations/update-agent-position`
- [POST] `core/flow-operations/add-connection-to-flow`
- [DELETE] `core/flow-operations/remove-connection-from-flow`
- [PUT] `core/flow-operations/update-connection-target`

---

## 8. ADK and Model Integration

**FR-2.4**, **FR-2.6**; out-of-scope: multiple models, tools.

- **ADK:** **Google's Agent Development Kit (ADK)** in Python. Use env var (`GOOGLE_API_KEY`) for credentials. In `runtime`, wrap ADK so: (a) credentials come from `os.environ`; (b) a single Google model id is hardcoded for all agents: **`gemini-1.5-flash`** (fast, cost-effective for MVP).
- **Per-agent config:** Pass each agent’s `system_instructions` (FR-2.7) into the model call. “Context provided to it” (FR-2.3): the trigger message or the upstream agent’s output as user/content in the conversation.
- **Tools:** Omit for MVP (not in FRs for initial release).

**Endpoints (ADK integration):**
- [POST] `runtime/executor/run-agent`
- [GET] `runtime/credentials/get-google-api-key`
- [POST] `runtime/credentials/validate-google-api-key`

---

## 9. Qt + Asyncio Integration (qasync)

**Technical decision:** Use **qasync** to integrate asyncio with Qt's event loop, allowing async executor code to run alongside the GUI without blocking.

### 9.1 Why qasync?

- **Single event loop:** Qt and asyncio share the same loop, so GUI stays responsive during async I/O (API calls).
- **Simpler than threading:** No thread safety concerns; direct `await` from GUI handlers.
- **Real-time events:** Executor callbacks/signals fire immediately on Qt's thread, enabling real-time visualization (FR-5.x).

### 9.2 Setup (M0, M3)

**App startup:**
**Endpoint:** [POST] `main/start-application`
```python
# ui/main.py
from PySide6.QtWidgets import QApplication
from qasync import QEventLoop
import asyncio

def main():
    app = QApplication([])
    
    # Install qasync: replaces asyncio's default loop with Qt-integrated loop
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    window = MainWindow()
    window.show()
    
    # Run Qt app (this also runs asyncio tasks)
    with loop:
        loop.run_forever()
```

### 9.3 GUI Calls Executor (M3, M4)

**Async-safe GUI handlers:**
```python
# ui/main.py
from qasync import asyncSlot

class MainWindow(QMainWindow):
    @asyncSlot()  # Decorator makes this async-safe
    async def on_run_button_clicked(self):
        # This doesn't block Qt - await yields to event loop
        result = await run_flow(
            flow=self.current_flow,
            entry_agent_id=self.selected_agent_id,
            user_message=self.get_user_message(),
            cancel_token=self.cancel_token,
            event_callback=self.on_executor_event
        )
        self.show_result(result)
```

### 9.4 Executor Events to GUI (M4, M5)

**Option 1: Direct callbacks (simple)**
```python
# runtime/executor.py
class Executor:
    def __init__(self, event_callback):
        self.event_callback = event_callback
    
    async def run_flow(self, ...):
        self.event_callback('agent_processing_started', agent_id='agent_1')
        # ... work ...
        self.event_callback('agent_processing_finished', agent_id='agent_1')

# ui/main.py
def handle_event(event_type, **kwargs):
    # Runs on Qt's thread - safe to update GUI
    if event_type == 'agent_processing_started':
        self.canvas.start_pulsating(kwargs['agent_id'])
```

**Option 2: Qt signals (more Qt-idiomatic)**
```python
# runtime/executor.py
from PySide6.QtCore import QObject, Signal

class Executor(QObject):
    agent_started = Signal(str)  # agent_id
    agent_finished = Signal(str)
    
    async def run_flow(self, ...):
        self.agent_started.emit('agent_1')
        # ... work ...
        self.agent_finished.emit('agent_1')

# ui/main.py
executor = Executor()
executor.agent_started.connect(self.canvas.start_pulsating)
```

### 9.5 Cancellation (FR-8.1)

```python
# ui/main.py
class MainWindow(QMainWindow):
    def __init__(self):
        self.cancel_token = asyncio.Event()  # Shared cancel flag
        self.current_task = None
    
    @asyncSlot()
    async def on_run_button_clicked(self):
        self.cancel_token.clear()
        self.current_task = asyncio.create_task(
            run_flow(..., cancel_token=self.cancel_token)
        )
        try:
            await self.current_task
        except asyncio.CancelledError:
            pass  # User clicked Stop
    
    def on_stop_button_clicked(self):
        self.cancel_token.set()
        if self.current_task:
            self.current_task.cancel()
```

**Note:** If ADK performs heavy CPU work, periodically yield with `await asyncio.sleep(0)` to keep GUI responsive.

---

## 10. Implementation Milestones

| Milestone | Goal | FRs | Deliverable |
|-----------|------|-----|-------------|
| **M0** | Desktop shell | FR-1.1, FR-1.2 (partial) | App window, empty canvas, runnable. |
| **M1** | Data + persistence | FR-7.1, FR-7.2, FR-2.1, FR-3.1 | `Flow`/`Agent`/`Connection` models; save/load JSON; load-on-startup behavior. |
| **M2** | Canvas + editing | FR-6.1–6.5, FR-2.7 | Nodes, edges, drag-to-connect, select, add/remove nodes and connections, edit system instructions in a panel. |
| **M3** | Single-agent run | FR-2.4–2.6, FR-2.5, FR-4.1 | ADK + Google model, env credentials, pre-run validation, “Run with message” to one agent; output in a simple area or log. |
| **M4** | Multi-agent run | FR-3.1–3.3, FR-4.2, FR-4.3 | Executor: fan-out, agent→agent; one trigger runs the graph. |
| **M5** | Run UX | FR-5.1–5.8, FR-8.1 | Pulsating (line in transit, agent border when thinking); Stop; hover for agent/line state. |
| **M6** | Polish | FR-7.2 (refine), remaining gaps | Load-on-startup UX, error handling, edge cases. |

---

## 11. FR Traceability

| FR | Milestone | Module / Note |
|----|-----------|---------------|
| FR-1.1 | M0 | `gui.main` — desktop app. |
| FR-1.2 | M0–M5 | `gui` — all creation, config, run in GUI. |
| FR-2.1 | M1, M2 | `core.models.Agent`; create in canvas. |
| FR-2.2 | M4 | `runtime.executor` — per-agent conversation/state. |
| FR-2.3 | M4 | `runtime.executor` — pass trigger or upstream output as input. |
| FR-2.4 | M3 | `runtime` + ADK — single Google model. |
| FR-2.5 | M3 | `runtime.validation` — pre-run; env + API check. |
| FR-2.6 | M3 | `runtime` — read from `os.environ`. |
| FR-2.7 | M2 | `gui.panels` — system instructions editor when agent selected. |
| FR-3.1 | M1, M2 | `core.models.Flow`; canvas represents it. |
| FR-3.2 | M4 | `runtime.executor` — iterate connections by `source_id`. |
| FR-3.3 | M4 | `runtime.executor` — one trigger, then traverse graph. |
| FR-4.1 | M3 | `gui` run input → `runtime` with entry agent + message. |
| FR-4.2 | M4 | `runtime.executor` — route output to `target_id`s. |
| FR-4.3 | M4 | Both paths in executor. |
| FR-5.1–5.3 | M2, M5 | `gui.canvas` — lines, borders, full flow visible. |
| FR-5.4 | M5 | `gui.canvas.edge` — animate on `data_in_transit`. |
| FR-5.5 | M5 | `gui.canvas.node` — animate border on `agent_processing_*`. |
| FR-5.6 | M5 | Combined effect of 5.4, 5.5. |
| FR-5.7 | M5 | Hover on node → tooltip from runtime-held agent state. |
| FR-5.8 | M5 | Hover on edge → tooltip from runtime-held connection state. |
| FR-6.1 | M2 | `gui.canvas` — drag from node, drop on node → new `Connection`. |
| FR-6.2 | M2 | `gui.canvas.node` — click to select. |
| FR-6.3 | M2 | Panel or context menu when agent/edge selected. |
| FR-6.4 | M2 | “Add agent” → new `Agent`, place on canvas. |
| FR-6.5 | M2 | Delete selected agent → remove from model and edges. |
| FR-7.1 | M1 | `persistence.storage` — JSON save/load. |
| FR-7.2 | M1, M6 | Startup: read “last path”, open or prompt. |
| FR-8.1 | M5 | `runtime.executor` — cancel task; GUI Stop button. |

---

## 12. Per-Milestone Implementation Notes

### M0 — Skeleton

- New PySide6 app; `QMainWindow`; central `QGraphicsView`/`QGraphicsScene`. No nodes yet.
- **qasync setup:** Install `qasync` package. In `ui/main.py`, set up `QEventLoop` and integrate with Qt's event loop (see §9.2). This enables async executor code in later milestones.
- Confirm Google ADK package is installable and credentials env var is documented.

### M1 — Data and Persistence

- Define `Agent`, `Connection`, `Flow` in `core.models` (dataclasses or Pydantic).
- `persistence.storage`: `load(path) -> Flow`, `save(flow, path)`. JSON schema as in §5.
- “Last opened” path: e.g. `~/.agenticflow/last` or app config. On startup: if `last` exists and file exists, open; else show empty flow. Menu: New, Open, Save, Save As.

### M2 — Canvas and Editing

- `AgentNode` on `QGraphicsScene` with `(x,y)`, border, label. `Connection` as `QGraphicsPathItem` between node centers/ports. Sync scene from `Flow` and back (position on move).
- Drag from node: start line on press, update on move, on release on another node create `Connection`. Click node → select, show side panel with `system_instructions` text edit.
- Toolbar: “Add agent” (place at center or click), “Delete” for selected node (and its connections). For connections: select edge or use panel to add/edit/delete by `source_id`/`target_id`.

### M3 — Single-Agent Run

- `runtime.executor`: `async def run_agent(agent_id, input_text, flow, get_credentials) -> output`. Use ADK with Google model, `system_instructions` from `Agent`, and `input_text` as user message. Credentials from `os.environ`.
- `runtime.validation`: `validate(flow) -> (ok: bool, message: str)`. Check env and optional lightweight API ping.
- **GUI integration:** Use `@asyncSlot()` decorator on the "Run" button handler. Call `await run_agent(...)` from the handler; qasync ensures GUI stays responsive during the async call (see §9.3).
- GUI: “Run with message” when one agent selected; input dialog; on Run, call `validate`; if ok, call `run_agent`, show result in a text area or log. No multi-agent yet.

### M4 — Multi-Agent Run

- `runtime.executor`: `async def run_flow(flow, entry_agent_id, user_message, cancel_token)`. Execute entry agent with `user_message`; on output, find `connections` with `source_id=agent_id`, for each `target_id` run that agent with the output as input. Recurse for fan-out. Respect `cancel_token` (FR-8.1) between agent steps.
- Emit `agent_processing_started/finished`, `data_in_transit`, `data_delivered`, `agent_output`, `connection_data` for GUI. Store latest agent and connection state for hover.

### M5 — Run UX

- **Stop:** “Stop” in GUI sets cancel; `run_flow` checks it and aborts.
- **Pulsating:** On `agent_processing_started(agent_id)`, start border animation for that node; on `agent_processing_finished` stop. On `data_in_transit(connection_id)` start line animation; on `data_delivered` stop. Only the line pulsates during transit (FR-5.4).
- **Hover:** On `QGraphicsItem.hoverEnter` for node/edge, show `QToolTip` or a small popover with the stored state for that agent or connection.

### M6 — Polish

- Startup: handle missing “last” file, invalid JSON, empty flow.
- Errors: validation failure, API errors, cancel; show in status bar or dialog.

---

## 13. Out-of-Scope (Do Not Implement for MVP)

From **functionalrequirements.md** §5:

- External triggers (webhooks, API).
- User-selectable models or multiple providers.
- GUI for defining/storing API credentials.
- Pause (only stop).

---

## 14. Document History

| Date | Change |
|------|--------|
| *(initial)* | Implementation plan from functionalrequirements.md. |
