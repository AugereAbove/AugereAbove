# AugereAbove

**Computer Science Student | Backend Developer | AI Systems & Automation**

I build backend services, developer tools, and automation systems, with a growing
focus on AI agents and model evaluation.

I care about software that is straightforward to run, test, and debug. My projects
use explicit validation, reproducible setups, and execution traces to make failures
something I can inspect and fix.

## Featured projects

### [Agent Eval](https://github.com/AugereAbove/agent-Eval)

A policy lookup runtime with an offline planner and an optional LLM planner.
Tool arguments are checked against JSON Schema before execution.

**Stack:** Python, JSON Schema, pytest, OpenAI Responses API.

**Engineering:** Planner and tool calls run in worker processes with deadlines.
The evaluation suite separates successful lookups, failure handling, and safety checks.

The default workflow runs without credentials. Provider integration is covered by
mocked tests; those tests are distinct from live model evaluations.

### [Multisite Content API](https://github.com/AugereAbove/multisite-content-api)

A Django REST API for managing pages across several sites, with draft publishing
and staff write permissions.

**Stack:** Python, Django, Django REST Framework, SQLite, Docker.

**Engineering:** Queries are scoped to the site in the URL, and a database constraint
keeps page slugs unique within each site. Tests cover visibility and write access.

A local development API with migrations, demo data, admin access, and CI.
Staff permissions are global; site specific editor roles are not implemented.

### [AI Browser Agent](https://github.com/AugereAbove/AI-browser-agent)

A browser automation runtime with bounded read sessions, a deterministic storefront
task runner, and persistent run history.

**Stack:** TypeScript, Node.js, Playwright, Zod, SQLite, Vitest.

**Engineering:** An independent verifier checks extracted products against the
fixture catalog before a run can be recorded as successful.

The fixture workflow is implemented. Model planning, a dashboard, and an approval
service remain planned capabilities.

### [AdaptiveEdge](https://github.com/AugereAbove/adaptive-Edge)

A library in progress for language model benchmarking and model selection under
quality, latency, and memory constraints.

**Stack:** Python, Pydantic, SQLite, Ollama integration.

**Engineering:** Benchmark observations are stored as immutable records. Selection
uses comparable historical evidence and can decline when constraints are unmet.

Benchmark runners, backend adapters, and selection components are implemented.
Its declared CLI entry point has no implementation in the current public source.

## Technical stack

### Programming languages

Python, TypeScript, JavaScript, and SQL.

### Backend frameworks

Django, Django REST Framework, and FastAPI.
FastAPI is used in the [Vibrato backend](https://github.com/AugereAbove/Vibrato).

### Developer tools and infrastructure

Git, GitHub Actions, Docker, Node.js, pnpm, and SQLite.
Local development environments and repeatable dependency installation.

### AI/ML engineering

LLM tool calling, JSON Schema and Pydantic validation, evaluation datasets,
Ollama integration, and constrained model selection.

### Testing and automation

pytest, Vitest, and Playwright.
API permission tests, deterministic browser fixtures, failure injection, and CI.

## Current focus

- AI agents whose tool use and outcomes can be evaluated separately.
- Backend architecture with clear data boundaries and permission rules.
- Reliable automation with bounded execution and useful failure records.
- Machine learning foundations and reproducible model benchmarking.

## Contact

I'm open to backend and software engineering opportunities, including remote roles,
and collaborations on developer tools, automation, and AI systems.

For project discussions, use the issue tracker in the relevant repository.
