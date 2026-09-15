# Plan: typed definition libraries (Python, then TypeScript) over a PostgreSQL copy of the graph

**Written:** 2026-09-13 by Claude, at the owner's request. **Status:** proposed; nothing below is done. **Executor:** to be assigned. **Owner approves each commit; do not commit.**

## Goal

Developers should be able to use the definitions as typed objects: load a finding class, walk to its elements and permitted values, its anatomic scope, its relationships, its component-of scope, and check a report Observation against them, from Python first and then from TypeScript. The definitions are read from a PostgreSQL database that is built from the canonical graph in git.

Two rules from the existing decisions shape everything here:

- **The source of truth stays the canonical JSON Lines graph in git.** The database is a derived copy, rebuilt from it, never edited by hand. (Architecture sketch in the current-understanding document; the round-trip contract in the structures document.)
- **Nothing is resolved only in a library or a loader.** What a library reports must be what the graph says, because the graph itself is consumed directly (decision record S36, the reviewer's constraint).

**Note, 2026-09-15.** Decision record S38 makes the reviewer's implementation (her Python specification and its JSON and OWL generators under `docs/next-gen-schema/alpha/`) the foundation going forward. This plan's models, loader, and query API must be reconciled with that specification rather than built beside it; the five decisions below stay open until the conceptual merge in `docs/plans/2026-09-15-commit-and-merge-path.md` has settled which form is canonical.

## Decisions the owner must make before Phase 1

Each is one question. Claude's recommendation is stated; none is decided.

1. **Where the code lives.** (a) A `packages/` workspace in this repository, next to the documents and the graph, so a change to the graph and a change to the library land in one commit. (b) A new package in the owner's OIFM workspace (`findingmodel`), which already has the uv workspace, Taskfile, Ruff, mypy, pytest, and a publish pipeline. *Recommendation: (a) now, because the graph format is still moving weekly and the library must move with it; extract later once the format settles.*
2. **The store.** The owner said "probably PostgreSQL". The alternative with a precedent is what OIFM does: build a single read-only database file (DuckDB), publish it, and have the library download and open it, so users need no server. PostgreSQL fits a shared, queryable, multi-user store and the reviewer's OWL and vendor questions; the file fits developers who just want the definitions. *Recommendation: PostgreSQL as asked, with the loader written so that the same tables can be produced in DuckDB later if a serverless form is wanted.*
3. **Package name and namespace.** Something that is not "findingmodel" and not "cde" alone. *Recommendation: decide the name with the reviewer, since it will be the vendor-facing name.*
4. **TypeScript scope for the first cut.** (a) Types only, generated from the Python models, so a TypeScript consumer of the JSON export is typed. (b) Types plus a database client. *Recommendation: (a) first; (b) once the Python query API is stable, so the two clients expose the same operations.*
5. **Whether report-plane shapes are included.** The Observation line shapes of the two-plane examples belong to the grammar (IHE), not the vocabulary. *Recommendation: include them as a separate module, because the scope and component-of checks need them, and the report pattern book will produce many.*

## What gets built

### 1. Python models (Pydantic v2)

One class per node type, mirroring the graph exactly: `FindingClass`, `Diagnosis`, `Grouping`, `DataElement` (with the categorical and quantitative shapes), `Value`, `AnatomicLocation`, `Concept`, `RelationshipType`, and `Edge` (type, from, to, optional id, properties). Field names and property names are the graph's; no renaming in the library. A `Graph` container holds nodes by id and edges, with the same order rules as the canonical form, so that `Graph.from_jsonl()` followed by `Graph.to_jsonl()` is byte-identical. The existing loader and validator in `tools/graph.py` become the first users of these models rather than a parallel implementation.

### 2. PostgreSQL schema and loader

A property-graph layout, because it mirrors the JSON Lines one-to-one and needs no migration when a node gains a property:

- `node(id, kind, props jsonb)` and `edge(type, from_id, to_id, id, props jsonb)`, with indexes on kind, type, from_id, to_id, and a GIN index on props.
- One SQL view per node kind exposing the common columns (`finding_class(id, name, entity_type, definition, ...)`), so ordinary SQL users see tables.
- Recursive views for the two walks the model relies on: `subtype_closure` (every ancestor over `SUBTYPE_OF`) and `anatomy_closure` (ancestors over `SUBTYPE_OF` and `PART_OF` together), which is how anatomic scope and component-of scope are checked.
- A loader command: read the canonical graph, replace the database contents in one transaction, record the source commit hash and load time in a `load` table.
- A round-trip check: dump the database back to JSON Lines and compare byte-for-byte with the source. This is the test that the store adds and loses nothing.

Apache AGE (openCypher on PostgreSQL) is not used in the first cut: recursive views cover the two walks we have, and AGE adds an extension dependency for every user. Revisit if queries outgrow SQL.

### 3. Python query API

Small and explicit; the operations the documents and the examples already perform:

- `get(id)`, `find(name)`, `by_kind(kind)`.
- `elements(class_id)` with their permitted values or quantity; `relationships(class_id)` grouped by type and direction; `anatomic_scope(class_id)`; `component_of_scope(class_id)`; `standard_clinical_metadata(class_id)`.
- `satisfies_scope(class_id, location_id)` and `satisfies_component_of_scope(component_class_id, container_class_id)`, both by walking the closures, both returning the path that satisfied.
- `validate_observation(...)` for a report line: the checks the report renderer performs today, moved into the library so the renderer calls it.

Access through SQLAlchemy 2 with psycopg 3, synchronous first. The API returns the Pydantic models, never raw rows.

### 4. TypeScript types

Generated, not hand-written: the Pydantic models emit JSON Schema (`model_json_schema()`), and `json-schema-to-typescript` compiles it to a `.d.ts` that is committed and checked in CI for drift against a fresh generation. Titles are stripped so types inline; optional fields drop `null`. The JSON export for vendors is the same JSON Schema, so a TypeScript consumer of the export is typed from day one. A TypeScript database client follows only after decision 4.

### 5. Tooling and process

uv workspace, Ruff, mypy strict, pytest, a Taskfile with `check`, `test`, `db:load`, `db:roundtrip`, `ts:generate`; the bundle checker gains one step, that the library loads the current graph and the round trip holds. Documentation: a reference page in the bundle for the library and the schema (structure), a how-to in the tools playbook (process), and a log entry per phase.

## Phases

0. Record the five decisions above in the decision record with the owner's words; name the package.
1. Models and `Graph` with the round-trip test against the current graph files; `tools/graph.py` rewired to use them; checker green.
2. PostgreSQL schema, loader, closures, round-trip check; a local database via a `docker compose` file for development.
3. Query API and validation; the report renderer calls the library for its checks; a CLI (`... get RDE2_000123`, `... scope-check ...`).
4. JSON Schema export; TypeScript types generated and committed; drift check.
5. Documentation and handoff; publish the Python package when the owner says so.

## Research notes (2026-09-13)

- Pydantic v2 generates JSON Schema from models directly; the pattern of Pydantic to JSON Schema to TypeScript is the standard route, with `json-schema-to-typescript` as the compiler and small conveniences such as `pydantic2-to-typescript` wrapping it ([Pydantic JSON Schema docs](https://pydantic.dev/docs/validation/latest/concepts/json_schema/), [pydantic2-to-typescript](https://pypi.org/project/pydantic2-to-typescript), [json-schema-to-typescript](https://github.com/bcherny/json-schema-to-typescript)).
- SQLAlchemy 2 with the psycopg 3 driver is the current mainstream pairing; SQLModel is a thin convenience over it for simple CRUD and not needed here ([discussion](https://github.com/fastapi/fastapi/discussions/9936), [comparison](https://tapanbasuli.medium.com/sqlalchemy-vs-sqlmodel-which-should-you-choose-for-your-python-project-7ea0b040af14)).
- Apache AGE is an active Apache top-level project supporting PostgreSQL 11 through 18 and available as a managed extension on Azure; it remains an option if openCypher is wanted later ([Apache AGE](https://age.apache.org/), [Azure](https://learn.microsoft.com/en-us/azure/postgresql/azure-ai/generative-ai-age-overview)).
- The owner's OIFM workspace (`findingmodel`) uses uv, Taskfile, Pydantic v2, Ruff at 120 columns, mypy, pytest with unit, integration, and eval tiers, and DuckDB files downloaded on demand for its index; no TypeScript exists there yet.
- Exact versions are pinned at execution time in `uv.lock` and `package.json`, not here.
