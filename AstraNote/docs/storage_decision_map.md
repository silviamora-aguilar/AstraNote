# AstraNote Storage Options Decision Map

This document visualizes storage options for AstraNote, with pros/cons and architecture considerations.

## 📊 Option landscape

```mermaid
flowchart TD
    A[JSON files (MVP)] -->|low complexity|B[SQLite]
    A -->|fast iteration|C[Key-Value Store]
    A -->|simple mapping|D[Hybrid JSON+Index]
    B -->|ORM abstraction|E[ORM (SQLAlchemy)]
    B -->|fast queries|F[Vector Store]
    B -->|sync support|G[Cloud/Remote DB]
    B -->|mobile-specific|H[Native (Realm/CoreData)]

    subgraph Primary Options
      A
      B
      C
      D
      E
      F
      G
      H
    end

    classDef good fill:#90EE90,stroke:#008000,stroke-width:2px;
    classDef warn fill:#FFD700,stroke:#DAA520,stroke-width:2px;
    classDef bad fill:#FFB6C1,stroke:#C71585,stroke-width:2px;

    class A good
    class B good
    class C warn
    class D warn
    class E good
    class F warn
    class G good
    class H warn
```

## ✅ Criteria summary

| Option | Storage interface | Persistency | Error handling | Privacy | Testability | Extensibility | Scalability / Concurrency |
|---|---|---|---|---|---|---|---|
| JSON files | simple CRUD + scan | cheap, file-based | manual recovery, atomic write required | local only, encryption needed | easy with temp dirs | backend swap possible | weak at high count/concurrency |
| SQLite | SQL/ORM-based | ACID | built-in, handle locks | local, encrypt at rest | in-memory DB tests | migrations, extensions | strong for local, moderate for concurrent writes |
| ORM | high-level models | DB-enabled | exception mapping | same as DB | good via fixtures | engine-agnostic | good for scale with right engine |
| Key-Value | key CRUD | fast key writes | engine-specific | can encrypt | simple | good for limited query | good for high throughput |
| Hybrid | file+index API | JSON+DB | consistency in two stores | moderate with E2E | moderate | incremental migration | moderate |
| Vector | sem search API | separate vector DB | service errors | semantic privacy concerns | can be mocked | augment only | scalable search |
| Cloud | network API | remote ACID | network/failover | strong with security | integration tests | multi-tenant | excellent concurrency |
| Native | platform API | native store | platform errors | good in app sandbox | hard cross-platform | platform specific | great for mobile |

## 📌 Implementation considerations

- Start with a `StorageBackend` interface in code and keep it small
- Define storage behavior fresh: `save_note`, `get_note`, `delete_note`, `list_notes`, `search_notes`
- Provide migration utility (JSON → SQLite/Cloud) later
- Add locks/atomic file operations to guard JSON path
- Keep backups for privacy and recovery

---

## 🧭 Recommendation for AstraNote

1. Begin with JSON for MVP, with strict atomic-write semantics
2. Add a SQLite backend in parallel, with consistent interface
3. Add optional vector store for semantic search
4. Add cloud sync once multi-user and device sync required
