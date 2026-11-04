# AgenticFlow

A planned desktop platform for creating and managing AI agents in real time. Users would place agents on a visual canvas, connect them into flows where one agent's output feeds others, and run and monitor those flows live. The repository currently holds the written requirements, the core data model and flow operations with unit tests, and a skeleton of the GUI.

## Stack

- Python 3.11
- PySide6 (Qt) for the desktop GUI, with `qasync` to run asyncio alongside the Qt event loop
- Google Agent Development Kit (`google-adk`) as the planned agent runtime
- pytest

## Running

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
pytest                          # run the unit tests
python main.py                  # launch the window (see Status)
```

The planned model credential is read from the `GOOGLE_API_KEY` environment variable; nothing is stored in the repo.

## Project layout

- `functionalrequirements.md` - product requirements
- `requirements-impl.md` - implementation plan and milestones
- `AI-Guidelines.md` - coding conventions (camelCase, type hints, a unit test per unit of code)
- `agents/` - role prompts for the AI coding agents used to build the project (requirement, developer, tester)
- `src/core/` - `Agent`, `Connection` and `Flow` dataclasses, factories, and flow operations (add and remove agents and connections)
- `src/runtime/` - credential check and an agent executor placeholder
- `src/ui/` - main window and an empty flow canvas scene
- `tests/` - unit tests for the core and the runtime prerequisites check

## Status

Work in progress, early stage. The core model and flow operations are implemented and tested. Agent execution is a stub that raises `NotImplementedError`, the canvas has no nodes or connections yet, and `src/ui/main.py` has an indentation error that must be fixed before the window will start.
