# AstraNote Storage Design

## Overview

AstraNote requires a simple, cross-platform storage system to persist user notes locally. This design focuses on minimal complexity while ensuring reliability, portability, and future extensibility.

## Goals

- Store notes with basic metadata (title, content, timestamps)
- Support cross-platform operation (Windows, macOS, Linux)
- Enable easy retrieval and basic search
- Provide a foundation for future features like cloud sync and encryption

## Core Data Model

### Note
Each note contains:

- `id`: Unique identifier (UUID)
- `title`: Note title (string)
- `content`: Full note text (string)
- `created_at`: Creation timestamp (ISO 8601)
- `updated_at`: Last modification timestamp (ISO 8601)
- `tags`: List of tag strings (optional)

Notes are stored as JSON objects for simplicity and portability.

## Storage Architecture

### Local File-Based Storage

- **Format**: JSON files for individual notes
- **Location**: User-specific directory (`~/.astranote/notes/`)
- **Naming**: Files named by note ID (e.g., `note-uuid.json`)
- **Index**: Simple JSON index file (`index.json`) mapping IDs to file paths and basic metadata

### Directory Structure

```
~/.astranote/
├── notes/
│   ├── note-uuid1.json
│   ├── note-uuid2.json
│   └── ...
└── index.json
```

### Operations

- **Save Note**: Write note JSON to file, update index
- **Load Note**: Read JSON from file using ID
- **List Notes**: Parse index for all notes
- **Search Notes**: Basic text search through titles and content
- **Delete Note**: Remove file and update index

## Cross-Platform Considerations

- Use `pathlib` for path handling
- Store data in user home directory (`Path.home()`)
- Ensure UTF-8 encoding for text
- Handle file system permissions gracefully

## Future Extensions

- **Database Backend**: Migrate to SQLite for better query performance
- **Cloud Sync**: Add sync adapters for remote storage
- **Encryption**: Implement optional note encryption
- **Attachments**: Support file attachments with notes
- **Vector Search**: Add AI-powered semantic search

## Implementation Notes

- Keep storage layer abstracted behind a simple interface
- Use environment variables for custom storage paths
- Include basic error handling for file operations
- Version the storage format for future migrations