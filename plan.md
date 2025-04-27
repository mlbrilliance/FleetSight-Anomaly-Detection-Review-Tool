# Project Plan & Requirements: FleetSight Anomaly Detection & Review Tool
**Version:** 1.4 (Explicit Ontology File Location)
**Date:** 2023-10-27
**Project Goal:** Develop a robust FastAPI service and accompanying beautiful React dashboard (Tailwind/shadcn/ui) to detect and allow review of anomalous fleet transaction data, leveraging ML, Supabase (initially with mocked data), deploying to DigitalOcean, and adhering to Project Synapse principles with strict structure, modularity, and **explicit use of the defined Project Ontology located in the `owl/` directory.**
**Target Technology:** Python/FastAPI (Backend), React/Vite/Tailwind/shadcn/ui/Lucide (Frontend), Scikit-learn/PyOD (ML), Supabase (Database via `supabase-py`), Docker, DigitalOcean Droplet.
**Project Ontology (Source of Truth):** Defined across files within the **`owl/` directory** (relative to project root). **ALL modes MUST reference these files for domain concepts, relationships, types, and terminology:**
    *   `owl/fleetsight-core-entities.ttl`
    *   `owl/fleetsight-anomaly.ttl`
    *   `owl/fleetsight-ml.ttl`
    *   `owl/fleetsight-system.ttl`
    *   `owl/fleetsight-users.ttl`
    *   `owl/fleetsight-problems.ttl`
**Cookiecutter Basis:** Use `tiangolo/full-stack-fastapi-postgresql` as structural foundation (adaptations required per `μT 0.1.1`).

---
**Legend:**
*   `μT`: Micro-Task ID
*   Ω: Responsible Mode: `🧠 ArchitectMind` (Plan, Design, Orchestrate, Enforce Standards & Ontology Use from `owl/`)
*   🛠️: Responsible Mode: `🛠️ ForgeAgent` (Implement, Self-Test[🎯🧪], Fix, Adhere to Specs/Limits/Ontology from `owl/`)
*   🛡️: Responsible Mode: `🛡️ Guardian` (Secure, Document, Integrate, Optimize, Deploy, Monitor, Verify Standards & Ontology Use from `owl/`)
*   [SAPPO]/[OWL]: Tag indicating direct reference/use of terms/definitions from the **Project Ontology files located in the `owl/` directory**.
*   `🎯🧪`: Targeted Testing. **MUST** validate against [OWL] definitions (from `owl/`) where applicable. Context provided by Ω.
*   `⚡️🔁`: Rapid Iteration Cycle managed by Ω, executed by 🛠️.
*   `<500L`: **Strict** max lines per file constraint.
*   `🚫🔑`: No hard-coded secrets constraint.
*   🧠RDD: Research task using MCP/Perplexity. Document findings.
---

## Phase 0: Project Scaffolding, Foundational Design, Ontology Definition & Standards Enforcement (Ω ArchitectMind Dominant)

*   **User Story Snippet:** As the development lead, I need a rigorously defined project structure, a comprehensive ontology located in `owl/`, core data models mapped precisely to that ontology, and enforced quality standards.
*   **`μT 0.1.1`:** **(Ω)** Generate initial project structure (adapted from Cookiecutter). Document adaptations. Output: Project structure plan. [SAPPO: :ProjectContext]
*   **`μT 0.1.2`:** **(Ω)** Define/enforce **strict folder structure**: `backend/`, `frontend/`, `shared_models/`, **`owl/` (MUST contain all `.ttl` ontology files)**, `infra/`, `.github/`, `.env.example`, `README.md`, etc. Output: Folder structure definition.
*   **`μT 0.1.3`:** **(🛡️)** Execute project setup/refactor per `μT 0.1.1`, `μT 0.1.2`. **Create the `owl/` directory.** Setup dependencies. Task=Setup/Refactor. Output: Clean project structure & base configs.
*   **`μT 0.2.1`:** **(Ω)** Define core data entities... Output: Initial entity list.
*   **`μT 0.2.2`:** **(Ω)** 🧠RDD. Formally define Project Ontology across 6 files **to be placed within the `owl/` directory**. Define Classes, Props etc. Output: Specs & Turtle content for files within `owl/`. [OWL: Full Ontology Definition]
*   **`μT 0.2.3`:** **(🛡️)** Create and syntactically validate all 6 `*.ttl` files **in the `owl/` directory** based on `μT 0.2.2` specs. Task=Document/Validate. Output: Verified Project Ontology files **inside `owl/`**. **This directory is now the single source of truth.**
*   **`μT 0.3.1`:** **(Ω)** Define Pydantic models (`shared_models/models.py`). **CRITICAL:** Each **MUST** map to Class/Property in the ontology **files within `owl/`**. Include RDF mapping/comment referencing specific `owl/` file + term. Strict validation per [OWL]. TDD anchors referencing [OWL]. Output: Strict `models.py` spec explicitly referencing **ontology in `owl/`**.
*   **`μT 0.3.2`:** **(🛠️)** Implement Pydantic models (`shared_models/models.py`) per `μT 0.3.1`. **Ensure mapping comments explicitly reference terms from `owl/` directory files.** `<500L`. Context for `🎯🧪`: Verify validation rules per TDD anchors & **corresponding [OWL] definitions in `owl/`**. `⚡️🔁`. Output: `shared_models/models.py` & tests validated against **ontology spec in `owl/`**. Confirmation of [OWL] (`owl/`) alignment in `📤`.
*   **`μT 0.4.1`:** **(Ω)** Design Supabase schemas. **Ensure structure reflects the Project Ontology definitions found in `owl/`**. Output: Supabase schema/migration spec, referencing [OWL] from `owl/`. [SAPPO: :DatabaseSchema]
*   **`μT 0.4.2`:** **(Ω)** Specify DB interface (`backend/db/interface.py`). **Methods MUST use Pydantic models (`μT 0.3.2`) aligned with [OWL] ontology from `owl/`**. Output: Strict DB Interface Spec referencing [OWL] (`owl/`) models.
*   **`μT 0.4.3`:** **(🛠️)** Implement mock (`backend/db/mock_db.py`) per `μT 0.4.2`. Ensure mock data respects [OWL] constraints **defined in `owl/`**. Context for `🎯🧪`: Test compliance, ensuring [OWL] (`owl/`)-aligned model I/O. `<500L`. `⚡️🔁`. Output: `backend/db/mock_db.py` & tests.
*   **`μT 0.5.1`:** **(Ω)** Specify configuration (`backend/config.py`). Output: Strict `config.py` spec. [SAPPO: :ConfigurationManagement]
*   **`μT 0.5.2`:** **(🛠️)** Implement `backend/config.py`. `<500L`. Context for `🎯🧪`: Verify loading. `⚡️🔁`. Output: `backend/config.py`, tests, `.env.example`.
*   **`μT 0.6.1`:** **(Ω)** Define quality standards: Add **"Mandatory adherence to Project Ontology located in the `owl/` directory"**. Update `README.md` spec including **Ontology section pointing to `owl/`**. Output: Quality Standard Doc, `README.md` spec, `.gitignore` spec (updated).
*   **`μT 0.6.2`:** **(🛡️)** Implement `README.md` & `.gitignore` (`μT 0.6.1`). Setup linters/formatters. Task=Document/Setup. Output: Project docs (referencing `owl/`), `.gitignore`, linter configs.

## Phase 1: Backend - Supabase Integration & Core Data API (Ω → 🛠️ → 🛡️)

*   **User Story Snippet:** As a Developer, I need to implement data handling that strictly follows the interfaces and models derived from our centrally located ontology in `owl/`.
*   **`μT 1.1.1`:** **(Ω)** Specify Supabase client impl (`backend/db/supabase_client.py`). **Mappings MUST align with ontology relationships defined in `owl/` and models (`μT 0.3.2`)**. Output: Spec referencing [OWL] from `owl/`.
*   **`μT 1.1.2`:** **(🛠️)** Implement `supabase_client.py` per `μT 1.1.1`. `<500L`. **Code MUST explicitly reflect [OWL] mapping from `owl/`**. Context for `🎯🧪`: Mock `supabase-py`; verify correct [OWL]-aligned parameters/mappings used. `⚡️🔁`. Output: `backend/db/supabase_client.py` & tests. Confirm [OWL](`owl/`) alignment in `📤`.
*   **`μT 1.2.1`:** **(Ω)** Specify FastAPI app setup (`backend/main.py`). Output: `main.py` spec.
*   **`μT 1.2.2`:** **(🛠️)** Implement `backend/main.py`. Context for `🎯🧪`: Verify app runs. `⚡️🔁`. Output: `backend/main.py` & tests.
*   **`μT 1.3.1`:** **(Ω)** Define API endpoint `/transactions` (POST). Request: List[:FleetTransaction] **(as defined by [OWL] in `owl/` via `shared_models`)**. Output: `/transactions` POST spec referencing [OWL]. [SAPPO: :APIEndpoint]
*   **`μT 1.3.2`:** **(🛠️)** Implement `/transactions` POST (`backend/api/v1/endpoints/transactions.py`). Use `db.interface`. **Validate request against [OWL](`owl/`)-derived Pydantic model**. `<500L`. Context for `🎯🧪`: Mock DB interface; verify validated, [OWL]-aligned data passed. `⚡️🔁`. Output: `.../transactions.py` & tests. Confirm `<500L` and [OWL](`owl/`) usage in `📤`.
*   **`μT 1.4.1`:** **(Ω)** Specify `preprocess_data` function. Define `ProcessedTransaction` **aligning with [OWL] concepts in `owl/`**. Output: Preprocessing spec referencing [OWL]. [SAPPO: :DataCleaning]
*   **`μT 1.4.2`:** **(🛠️)** Implement `preprocess_data` in `backend/processing/cleaner.py`. `<500L`. **Align logic with [OWL] field definitions from `owl/`**. Context for `🎯🧪`: Verify per TDD anchors & [OWL] context. `⚡️🔁`. Output: `processing/cleaner.py` & tests.
*   **`μT 1.4.3`:** **(Ω)** Update `/transactions` POST spec (`μT 1.3.1`) integrating `preprocess_data`. Output: Updated spec.
*   **`μT 1.4.4`:** **(🛠️)** Modify `/transactions` POST (`μT 1.3.2`). Context for `🎯🧪`: Verify call, processed [OWL]-aligned data passed. `⚡️🔁`. Output: Updated `.../transactions.py` & tests.
*   **`μT 1.5.1`:** **(Ω)** Specify security review for ingestion pipeline. Check validation against [OWL]-derived models **from `owl/`**. Output: Security review spec.
*   **`μT 1.5.2`:** **(🛡️)** Execute security review (`μT 1.5.1`). **Verify data handling aligns with implicit security needs defined by [OWL] (`owl/`)**. Task=Secure. Output: Security report.

*(This explicit referencing of the ontology location `owl/` should be consistently applied to ALL subsequent Phases and Micro-Tasks involving domain models, data handling, feature engineering, testing against specs, security reviews, and documentation.)*

**Change Summary:**

*   Added the `owl/` directory to the defined folder structure (`μT 0.1.2`, `μT 0.1.3`).
*   Specified that all `.ttl` files must reside in `owl/` (`μT 0.2.2`, `μT 0.2.3`).
*   Updated tasks involving ontology reference (`μT 0.3.1`, `μT 0.3.2`, `μT 0.4.1`, `μT 0.4.2`, `μT 0.6.1`, `μT 1.1.1`, `μT 1.1.2`, `μT 1.3.1`, `μT 1.3.2`, `μT 1.4.1`, `μT 1.4.2`, `μT 1.5.1`, `μT 1.5.2`, etc.) to explicitly state that the definitions are sourced **from the files within the `owl/` directory**.
*   Reinforced this in the Legend and introductory statements.

This makes it unambiguous for all modes where the authoritative source of domain knowledge resides.```markdown
# Project Plan & Requirements: FleetSight Anomaly Detection & Review Tool
**Version:** 1.4 (Explicit Ontology File Location)
**Date:** 2023-10-27
**Project Goal:** Develop a robust FastAPI service and accompanying beautiful React dashboard (Tailwind/shadcn/ui) to detect and allow review of anomalous fleet transaction data, leveraging ML, Supabase (initially with mocked data), deploying to DigitalOcean, and adhering to Project Synapse principles with strict structure, modularity, and **explicit use of the defined Project Ontology located in the `owl/` directory.**
**Target Technology:** Python/FastAPI (Backend), React/Vite/Tailwind/shadcn/ui/Lucide (Frontend), Scikit-learn/PyOD (ML), Supabase (Database via `supabase-py`), Docker, DigitalOcean Droplet.
**Project Ontology (Source of Truth):** Defined across files within the **`owl/` directory** (relative to project root). **ALL modes MUST reference these files for domain concepts, relationships, types, and terminology:**
    *   `owl/fleetsight-core-entities.ttl`
    *   `owl/fleetsight-anomaly.ttl`
    *   `owl/fleetsight-ml.ttl`
    *   `owl/fleetsight-system.ttl`
    *   `owl/fleetsight-users.ttl`
    *   `owl/fleetsight-problems.ttl`
**Cookiecutter Basis:** Use `tiangolo/full-stack-fastapi-postgresql` as structural foundation (adaptations required per `μT 0.1.1`).

---
**Legend:**
*   `μT`: Micro-Task ID
*   Ω: Responsible Mode: `🧠 ArchitectMind` (Plan, Design, Orchestrate, Enforce Standards & Ontology Use from `owl/`)
*   🛠️: Responsible Mode: `🛠️ ForgeAgent` (Implement, Self-Test[🎯🧪], Fix, Adhere to Specs/Limits/Ontology from `owl/`)
*   🛡️: Responsible Mode: `🛡️ Guardian` (Secure, Document, Integrate, Optimize, Deploy, Monitor, Verify Standards & Ontology Use from `owl/`)
*   [SAPPO]/[OWL]: Tag indicating direct reference/use of terms/definitions from the **Project Ontology files located in the `owl/` directory**.
*   `🎯🧪`: Targeted Testing. **MUST** validate against [OWL] definitions (from `owl/`) where applicable. Context provided by Ω.
*   `⚡️🔁`: Rapid Iteration Cycle managed by Ω, executed by 🛠️.
*   `<500L`: **Strict** max lines per file constraint.
*   `🚫🔑`: No hard-coded secrets constraint.
*   🧠RDD: Research task using MCP/Perplexity. Document findings.
---

## Phase 0: Project Scaffolding, Foundational Design, Ontology Definition & Standards Enforcement (Ω ArchitectMind Dominant)

*   **User Story Snippet:** As the development lead, I need a rigorously defined project structure, a comprehensive ontology located in `owl/`, core data models mapped precisely to that ontology, and enforced quality standards.
*   **`μT 0.1.1`:** **(Ω)** Generate initial project structure (adapted from Cookiecutter). Document adaptations. Output: Project structure plan. [SAPPO: :ProjectContext]
*   **`μT 0.1.2`:** **(Ω)** Define/enforce **strict folder structure**: `backend/`, `frontend/`, `shared_models/`, **`owl/` (MUST contain all `.ttl` ontology files)**, `infra/`, `.github/`, `.env.example`, `README.md`, etc. Output: Folder structure definition.
*   **`μT 0.1.3`:** **(🛡️)** Execute project setup/refactor per `μT 0.1.1`, `μT 0.1.2`. **Create the `owl/` directory.** Setup dependencies. Task=Setup/Refactor. Output: Clean project structure & base configs.
*   **`μT 0.2.1`:** **(Ω)** Define core data entities... Output: Initial entity list.
*   **`μT 0.2.2`:** **(Ω)** 🧠RDD. Formally define Project Ontology across 6 files **to be placed within the `owl/` directory**. Define Classes, Props etc. Output: Specs & Turtle content for files within `owl/`. [OWL: Full Ontology Definition]
*   **`μT 0.2.3`:** **(🛡️)** Create and syntactically validate all 6 `*.ttl` files **in the `owl/` directory** based on `μT 0.2.2` specs. Task=Document/Validate. Output: Verified Project Ontology files **inside `owl/`**. **This directory is now the single source of truth.**
*   **`μT 0.3.1`:** **(Ω)** Define Pydantic models (`shared_models/models.py`). **CRITICAL:** Each **MUST** map to Class/Property in the ontology **files within `owl/`**. Include RDF mapping/comment referencing specific `owl/` file + term. Strict validation per [OWL]. TDD anchors referencing [OWL]. Output: Strict `models.py` spec explicitly referencing **ontology in `owl/`**.
*   **`μT 0.3.2`:** **(🛠️)** Implement Pydantic models (`shared_models/models.py`) per `μT 0.3.1`. **Ensure mapping comments explicitly reference terms from `owl/` directory files.** `<500L`. Context for `🎯🧪`: Verify validation rules per TDD anchors & **corresponding [OWL] definitions in `owl/`**. `⚡️🔁`. Output: `shared_models/models.py` & tests validated against **ontology spec in `owl/`**. Confirmation of [OWL] (`owl/`) alignment in `📤`.
*   **`μT 0.4.1`:** **(Ω)** Design Supabase schemas. **Ensure structure reflects the Project Ontology definitions found in `owl/`**. Output: Supabase schema/migration spec, referencing [OWL] from `owl/`. [SAPPO: :DatabaseSchema]
*   **`μT 0.4.2`:** **(Ω)** Specify DB interface (`backend/db/interface.py`). **Methods MUST use Pydantic models (`μT 0.3.2`) aligned with [OWL] ontology from `owl/`**. Output: Strict DB Interface Spec referencing [OWL] (`owl/`) models.
*   **`μT 0.4.3`:** **(🛠️)** Implement mock (`backend/db/mock_db.py`) per `μT 0.4.2`. Ensure mock data respects [OWL] constraints **defined in `owl/`**. Context for `🎯🧪`: Test compliance, ensuring [OWL] (`owl/`)-aligned model I/O. `<500L`. `⚡️🔁`. Output: `backend/db/mock_db.py` & tests.
*   **`μT 0.5.1`:** **(Ω)** Specify configuration (`backend/config.py`). Output: Strict `config.py` spec. [SAPPO: :ConfigurationManagement]
*   **`μT 0.5.2`:** **(🛠️)** Implement `backend/config.py`. `<500L`. Context for `🎯🧪`: Verify loading. `⚡️🔁`. Output: `backend/config.py`, tests, `.env.example`.
*   **`μT 0.6.1`:** **(Ω)** Define quality standards: Add **"Mandatory adherence to Project Ontology located in the `owl/` directory"**. Update `README.md` spec including **Ontology section pointing to `owl/`**. Output: Quality Standard Doc, `README.md` spec, `.gitignore` spec (updated).
*   **`μT 0.6.2`:** **(🛡️)** Implement `README.md` & `.gitignore` (`μT 0.6.1`). Setup linters/formatters. Task=Document/Setup. Output: Project docs (referencing `owl/`), `.gitignore`, linter configs.

## Phase 1: Backend - Supabase Integration & Core Data API (Ω → 🛠️ → 🛡️)

*   **User Story Snippet:** As a Developer, I need to implement data handling that strictly follows the interfaces and models derived from our centrally located ontology in `owl/`.
*   **`μT 1.1.1`:** **(Ω)** Specify Supabase client impl (`backend/db/supabase_client.py`). **Mappings MUST align with ontology relationships defined in `owl/` and models (`μT 0.3.2`)**. Output: Spec referencing [OWL] from `owl/`.
*   **`μT 1.1.2`:** **(🛠️)** Implement `supabase_client.py` per `μT 1.1.1`. `<500L`. **Code MUST explicitly reflect [OWL] mapping from `owl/`**. Context for `🎯🧪`: Mock `supabase-py`; verify correct [OWL]-aligned parameters/mappings used. `⚡️🔁`. Output: `backend/db/supabase_client.py` & tests. Confirm [OWL](`owl/`) alignment in `📤`.
*   **`μT 1.2.1`:** **(Ω)** Specify FastAPI app setup (`backend/main.py`). Output: `main.py` spec.
*   **`μT 1.2.2`:** **(🛠️)** Implement `backend/main.py`. Context for `🎯🧪`: Verify app runs. `⚡️🔁`. Output: `backend/main.py` & tests.
*   **`μT 1.3.1`:** **(Ω)** Define API endpoint `/transactions` (POST). Request: List[:FleetTransaction] **(as defined by [OWL] in `owl/` via `shared_models`)**. Output: `/transactions` POST spec referencing [OWL]. [SAPPO: :APIEndpoint]
*   **`μT 1.3.2`:** **(🛠️)** Implement `/transactions` POST (`backend/api/v1/endpoints/transactions.py`). Use `db.interface`. **Validate request against [OWL](`owl/`)-derived Pydantic model**. `<500L`. Context for `🎯🧪`: Mock DB interface; verify validated, [OWL]-aligned data passed. `⚡️🔁`. Output: `.../transactions.py` & tests. Confirm `<500L` and [OWL](`owl/`) usage in `📤`.
*   **`μT 1.4.1`:** **(Ω)** Specify `preprocess_data` function. Define `ProcessedTransaction` **aligning with [OWL] concepts in `owl/`**. Output: Preprocessing spec referencing [OWL]. [SAPPO: :DataCleaning]
*   **`μT 1.4.2`:** **(🛠️)** Implement `preprocess_data` in `backend/processing/cleaner.py`. `<500L`. **Align logic with [OWL] field definitions from `owl/`**. Context for `🎯🧪`: Verify per TDD anchors & [OWL] context. `⚡️🔁`. Output: `processing/cleaner.py` & tests.
*   **`μT 1.4.3`:** **(Ω)** Update `/transactions` POST spec (`μT 1.3.1`) integrating `preprocess_data`. Output: Updated spec.
*   **`μT 1.4.4`:** **(🛠️)** Modify `/transactions` POST (`μT 1.3.2`). Context for `🎯🧪`: Verify call, processed [OWL]-aligned data passed. `⚡️🔁`. Output: Updated `.../transactions.py` & tests.
*   **`μT 1.5.1`:** **(Ω)** Specify security review for ingestion pipeline. Check validation against [OWL]-derived models **from `owl/`**. Output: Security review spec.
*   **`μT 1.5.2`:** **(🛡️)** Execute security review (`μT 1.5.1`). **Verify data handling aligns with implicit security needs defined by [OWL] (`owl/`)**. Task=Secure. Output: Security report.

*(This explicit referencing of the ontology location `owl/` should be consistently applied to ALL subsequent Phases and Micro-Tasks involving domain models, data handling, feature engineering, testing against specs, security reviews, and documentation.)*

**Change Summary:**

*   Added the `owl/` directory to the defined folder structure (`μT 0.1.2`, `μT 0.1.3`).
*   Specified that all `.ttl` files must reside in `owl/` (`μT 0.2.2`, `μT 0.2.3`).
*   Updated tasks involving ontology reference (`μT 0.3.1`, `μT 0.3.2`, `μT 0.4.1`, `μT 0.4.2`, `μT 0.6.1`, `μT 1.1.1`, `μT 1.1.2`, `μT 1.3.1`, `μT 1.3.2`, `μT 1.4.1`, `μT 1.4.2`, `μT 1.5.1`, `μT 1.5.2`, etc.) to explicitly state that the definitions are sourced **from the files within the `owl/` directory**.
*   Reinforced this in the Legend and introductory statements.