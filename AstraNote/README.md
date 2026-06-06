# AstraNotes

AstraNotes is a local, single-user note-taking MVP for browser-based desktop workflows. It focuses on fast note capture, private-note protection, an English/Spanish UI toggle, and a clean review trail across requirements, planning, and acceptance documents.

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

1. Install dependencies: `pip install -r requirements.txt`
2. Start the app: `uvicorn src.main:app --reload`
3. Open the local address printed by Uvicorn in your browser

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

- Python 3.9+
- A modern browser such as Chrome, Firefox, or Safari

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start the application

```bash
uvicorn src.main:app --reload
```

Then open the local app in your browser at the address printed by Uvicorn.

## Test the MVP

```bash
pytest tests/
```

## Design References

- [docs/sdlc-document-map.html](docs/sdlc-document-map.html) for the full document map
- [docs/product-requirements-document.md](docs/product-requirements-document.md) for the product framing
- [docs/executive-one-pager.md](docs/executive-one-pager.md) for the short project overview
- [docs/storage_design.md](docs/storage_design.md) for storage tradeoffs and rationale
- [planning/requirements.md](planning/requirements.md) for the canonical requirement baseline

## Runtime Data

The application creates and updates runtime data under the `data/` directory. On first launch, the app should create what it needs automatically.
