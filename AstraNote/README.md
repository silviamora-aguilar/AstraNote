# AstraNotes

A web-based multi-user note-taking application with private-note encryption, Markdown authoring, and secure server-side storage.

## Project Structure

```
AstraNotes/
├── src/                 # Main application source code
├── tests/               # Unit, integration, and security tests
├── docs/                # Architecture and design documentation
├── data/                # Runtime data (notes.json, audit-log.jsonl, security-state.json, config.json)
├── planning/            # Requirements, user stories, backlog, sprint plans, test plan, release gates
├── README.md            # This file
├── requirements.txt     # Python dependencies
├── setup.py             # Package configuration
└── .gitignore           # Git ignore patterns
```

## MVP Features

- Create, edit, delete, and search notes
- Markdown-compatible body formatting (bold, italic, underline, bullet lists, checklists)
- Note privacy toggle with passphrase-based unlock and encrypted-at-rest storage
- Soft delete with 30-day retention and restore
- Audit logging for all note operations
- Browser-based experience with authenticated user accounts and per-user data isolation

## Out of Scope for MVP

- Native desktop client packaging
- AI summarization or semantic search
- Native mobile application
- Per-note key isolation (Post-MVP)

## Getting Started

### Requirements
- Python 3.9+
- pip or conda
- Browser for frontend testing (Chrome, Firefox, or Safari)

### Installation

```bash
pip install -r requirements.txt
```

### Running the Application

```bash
uvicorn src.main:app --reload
```

## Development

### Running Tests

```bash
pytest tests/
```

### Storage Design

- See `docs/storage_design.md` for the architecture and implementation plan for AstraNote storage.

### Contributing

Please follow the guidelines in CONTRIBUTING.md (when created)

## License

MIT License - See LICENSE file for details
