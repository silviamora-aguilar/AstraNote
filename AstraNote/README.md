# AstraNotes

AstraNotes is a local, single-user note-taking MVP for browser-based desktop workflows. It focuses on fast note capture, private-note protection, an English/Spanish UI toggle, and a clean review trail across requirements, planning, and acceptance documents.

## Design References

- [docs/sdlc-document-map.html](docs/sdlc-document-map.html) for the full document map ([Open in browser](https://silviamora-aguilar.github.io/AstraNote/AstraNote/docs/sdlc-document-map.html), [Backup browser link](https://htmlpreview.github.io/?https://raw.githubusercontent.com/silviamora-aguilar/AstraNote/main/AstraNote/docs/sdlc-document-map.html))
- [Live demo walkthrough (.mov)](https://drive.google.com/file/d/1XBxujhVUkyjuJhzpCbLRhAN8jt9h8tmI/view?usp=drive_link) for the presentation recording

## Project Status

Delivered MVP baseline for local browser use on `127.0.0.1`. Multi-user accounts, shared ownership scoping, and other expansion items remain Post-MVP.

## Technology Stack

- FastAPI for the backend application and route handling
- Jinja2 + HTMX for server-rendered UI interactions
- SQLite for local persistence during the MVP baseline
- Structured encryption and PIN handling for private-note content

## MVP Snapshot

The delivered MVP includes:

- Create, edit, delete, restore, list, and search notes
- Limited markdown-style body authoring with bullet lists and checklists
- Private-note toggles with PIN-based unlock and encrypted-at-rest storage
- Soft delete with Trash review and 15-day retention
- Audit and diagnostic logging for note operations
- English/Spanish UI text toggle
- Local browser delivery on 127.0.0.1 for the course review baseline

## Quick Start

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies: `python -m pip install -r requirements.txt`
3. Start the app: `python -m uvicorn src.main:app --reload`
4. Open http://127.0.0.1:8000/ui/notes in your browser

## Feature Highlights

- Browser-first note editing and review flow
- PIN-protected private notes with encrypted storage
- Trash workflow for safe restore and purge behavior
- Requirements, planning, and acceptance artifacts aligned to the implemented MVP
- Spanish and English UI text support for the browser interface

## What is out of scope for this MVP

- Multi-user accounts, login, and shared ownership scoping
- Device sync and collaboration
- Native mobile packaging
- Per-note key isolation
- Plugin architecture or advanced content types such as image paste

## Repository Layout

```
AstraNotes/
├── src/                 # Application source code
├── tests/               # Unit, integration, and security tests
├── docs/                # Product, architecture, and review documents
├── planning/            # Requirements, backlog, traceability, gates, and plans
├── assets/              # Shared visual assets such as the giraffe logo
├── README.md            # Project overview
├── requirements.txt     # Python dependencies
├── pyproject.toml       # Tooling and project metadata
└── setup.py             # Package configuration
```

## Run the App

### Prerequisites

- Python 3.11+
- A modern browser such as Chrome, Firefox, or Safari

### Install dependencies

```bash
python -m pip install -r requirements.txt
```

### Start the application

```bash
python -m uvicorn src.main:app --reload
```

Then open the local app in your browser at the address printed by Uvicorn.

No environment variables are required for local execution; defaults are applied automatically.

## Test the MVP

```bash
pytest tests/
```

## Runtime Data

The application creates and updates runtime data under the `data/` directory. On first launch, the app should create what it needs automatically.
