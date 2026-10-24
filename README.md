# AI-SDLC-Docs

A lightweight repository of AI-assisted software development lifecycle (SDLC) prompts and standards-aligned checklist artifacts for architecture, design, database modeling, UX, and test planning.

## Purpose

This repo provides reusable prompt templates and supporting checklist documents that help generate structured engineering outputs such as:

- API design documents
- Blueprint / architecture design artifacts
- UML diagrams
- Database design specifications
- UI/UX design prompts
- Test plans and QA documentation

The materials are intended to support teams working with AI tools to create standards-based software engineering artifacts faster and more consistently.

## Repository Contents

Documents are organized by SDLC phase, in folders matching the phase numbers in [AI_SDLC-SOP.md](./AI_SDLC-SOP.md):

| Folder | SDLC phase | Contents |
|---|---|---|
| [`requirements/`](./requirements) | Requirements and discovery (5.2) | Business requirements document template |
| [`analysis/`](./analysis) | Analysis (5.3) | BRD and PRD prompts and the requirements checklist |
| [`design/`](./design) | Design, modeling (5.4) | SAD, blueprint, UML diagram, API, database and UI/UX prompts with their checklists |
| [`verification/`](./verification) | Verification and testing (5.7) | Test plan prompt and checklist |

### Prompt Templates

Prompt files for common SDLC activities, kept in the folder of the phase that uses them:

- `requirements/` — the BRD template
- `analysis/BRD_Elicitation_Prompt_IEEE_standard.md`
- `analysis/BRD_Prompt_IEEE_standard.md`
- `analysis/PRD_prompt.md`, `analysis/PRD_Prompt_IEEE_standard.md`, `analysis/PRD_Prompt_with_template.md`
- `design/SAD_prompt.md`, `design/SAD_Prompt_IEEE_standard.md`, `design/SAD_Prompt_with_template_.md`
- `design/bluePrint_design_prompt.md`
- `design/classDiagram_prompt.md`, `design/componentDiagram_prompt.md`, `design/deploymentDiagram_prompt.md`
- `design/sequenceDiagram_prompt.md`, `design/activityDiagram_prompt.md`, `design/useCase_prompt.md`
- `design/apiDesign_prompt.md`, `design/UI-UX-Design_prompt.md`
- `design/databaseDesign_SQL_prompt.md`, `design/databaseDesign_NoSQL_prompt.md`, `design/databaseDesign_GraphrDB_prompt.md`, `design/databaseDesign_VectorDB_prompt.md`
- `verification/testPlan_prompt.md`

### Checklist Artifacts

Supporting checklist spreadsheets sit next to the prompts they validate:

- `analysis/PRD_IEEE_29148_Checklist.xlsx`
- `design/BluePrint_Design_IEEE_1016_2009_Checklist.xlsx`, `design/SAD_IEEE_1016_Checklist.xlsx`
- `design/Class_Diagram_UML2.0_Checklist.xlsx`, `design/Component_Diagram_UML2.0_Checklist.xlsx`, `design/Deployment_Diagram_UML2.0_Checklist.xlsx`
- `design/Sequence_Diagram_UML2.0_Checklist.xlsx`, `design/Activity_Diagram_UML2.0_Checklist.xlsx`, `design/UseCase_Document_UML2.0_Checklist.xlsx`
- `design/API_Design_IEEE-1016-2009Checklist.xlsx`, `design/UI_UX_Design_IEEE-1016-2009_Checklist.xlsx`
- `design/Database_Design_Checklist.xlsx`, `design/Polyglot_DB_Design_Checklist.xlsx`, `design/Checklist_Database Design Review.xlsx`
- `verification/Test_Plan_IEEE_829_Checklist.xlsx`

### Standards:

- IEEE 1016-2009, IEEE 829, IEEE 29148
- UML 2.0

## Typical Usage

1. Choose the prompt for the phase you are working in, from that phase's folder.
2. Fill in the placeholder system or project details in the prompt.
3. Use the prompt with your preferred AI assistant or generation workflow.
4. Save the generated output into the target project's `docs/<phase>` folder as defined in [AI_SDLC-SOP.md](./AI_SDLC-SOP.md).
5. Use the spreadsheet checklists to validate completeness and standards alignment.

## Suggested Workflow

- Requirements and architecture inputs -> blueprint / API / database prompts
- Design and user experience inputs -> UI/UX prompt
- Verification and quality inputs -> test plan prompt

## Notes

This repository is organized as a collection of reusable prompts and review checklists. It is best used as a starting point for generating structured SDLC documentation rather than as a completed product application.

## Application code: "Chat với tài liệu" (MVP)

Besides the prompts, this repository now also holds the source code of the MVP described in [`docs/requirements/`](./docs/requirements) and planned in [`docs/implement/`](./docs/implement). The plan is in [`implement_plan.md`](./docs/implement/implement_plan.md); one file per task is in [`docs/implement/tasks/`](./docs/implement/tasks).

| Folder | Content |
|---|---|
| [`backend/`](./backend) | Python 3.12 backend (FastAPI, SQLAlchemy, Alembic, pgvector), worker, adapters for Claude, local embedding, S3, local/OIDC login |
| [`frontend/`](./frontend) | React 18 + TypeScript + Vite: screens S-01..S-07 |
| [`evaluation/`](./evaluation) | Quality evaluation runner, datasets, spikes (PDF extraction, embedding retrieval, generation) |
| [`e2e/`](./e2e) | Playwright end-to-end tests (with axe accessibility checks) |
| [`deploy/`](./deploy) | Docker Compose (dev, E2E override, monitoring profile), Dockerfiles, nginx, Prometheus alert rules |

The technology stack is a proposal pending decision gate G0 (see `implement_plan.md`, section 1). Operating guide: [`docs/implement/ops_runbook.md`](./docs/implement/ops_runbook.md). Data handling record: [`docs/implement/data_handling.md`](./docs/implement/data_handling.md).

### Prerequisites

- Docker 24+ with Docker Compose v2 (enough to run everything; no local Python needed)
- Node.js 20+ and npm (frontend checks, E2E)
- Optional: Python 3.12 to run backend tools without Docker

### Run the application locally

```bash
docker compose -f deploy/docker-compose.yml up -d --build --wait
docker compose -f deploy/docker-compose.yml exec backend python -m app.cli create-admin admin
# create a BD user, then open http://localhost:5173
docker compose -f deploy/docker-compose.yml exec backend python -m app.cli create-user an.nguyen bd
```

Defaults come from `deploy/env.example`; put overrides and secrets (e.g. `ANTHROPIC_API_KEY`, `ANSWER_PROVIDER=claude`, ports) in `deploy/.env` (git-ignored). The first start downloads the embedding model `BAAI/bge-m3` (~2.3 GB) once (service `model-download`). Without an API key keep `ANSWER_PROVIDER=fake` (canned answers with real citations, for UI work).

### Run the checks

Backend, in Docker (needs `docker compose -f deploy/docker-compose.yml up -d postgres objectstore`):

```bash
scripts/backend-docker.sh                 # ruff, mypy, import-linter, all pytest (unit, integration, security)
scripts/backend-docker.sh pytest tests/unit -q
```

Backend without Docker (from `backend/`): `pip install -e ".[dev]"` then `ruff check app tests alembic`, `mypy`, `lint-imports`, `pytest`. Integration tests start PostgreSQL (pgvector) and an S3 store with testcontainers, or use `TEST_DATABASE_URL` / `TEST_S3_ENDPOINT_URL` when set.

Frontend (from `frontend/`): `npm ci && npm run lint && npm run typecheck && npm test`. After an API change: export OpenAPI with `python backend/scripts/export_openapi.py frontend/src/api/openapi.json`, then `npm run gen:api`.

End-to-end (fake AI adapter, seeded accounts):

```bash
docker compose -f deploy/docker-compose.yml -f deploy/docker-compose.e2e.yml up -d --build --wait
cd e2e && npm ci && npx playwright install chromium && npx playwright test
```

Evaluation: `python evaluation/run_eval.py --dataset evaluation/datasets/sample.jsonl --fake` (see `evaluation/README.md`).

### Dependency rules

`backend/.importlinter` enforces: modules in `app/modules` must not import `app/adapters`, and `app/api` must not import `app/adapters` directly. Business modules depend only on the ports in `app/ports`; adapters are wired in at `app/container.py`.

## License

This repository does not currently declare a specific license. If you plan to redistribute or reuse it publicly, add an appropriate license file and terms.
