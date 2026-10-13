<!--
Sync Impact Report:
- Version Change: 0.0.0 (Unratified Template) → 1.0.0
- Ratification Date: 2026-10-13
- Modified Principles:
  - [PRINCIPLE_1_NAME] → I. Radical Simplicity & Minimality
  - [PRINCIPLE_2_NAME] → II. Polymorphic Architecture via Protocols
  - [PRINCIPLE_3_NAME] → III. Test-Driven Non-Mocking Integrity
  - [PRINCIPLE_4_NAME] → IV. Environment Isolation & Execution Safety
  - [PRINCIPLE_5_NAME] → V. Fail-Fast & Transparent Error Propagation
- Added Sections:
  - Technology Stack & Implementation Standards
  - Analysis & Quality Verification Workflow
- Removed Sections: None
- Deferred Items / TODOs: None
-->

# mini-SWE-agent Constitution

## Core Principles

### I. Radical Simplicity & Minimality
The primary objective of this repository is to provide the simplest, smallest, and most readable AI
software engineering agent.
- Code MUST be concise, minimal, and direct.
- Developers and agents MUST avoid initializing intermediate variables solely to pass them into a
  function (e.g., prefer `Class(func())` over temporary assignments).
- Defensive over-engineering, unnecessary abstraction layers, and bloated wrappers are prohibited.
- Comments MUST be kept to a minimum, highlighting only logically complex or non-obvious segments.
- Rationale: A lean codebase maximizes maintainability, comprehension, and benchmark reproducibility.

### II. Polymorphic Architecture via Protocols
The system MUST embrace runtime polymorphism while keeping every individual component simple.
- Base interfaces and protocols MUST be centralized in `minisweagent/__init__.py`.
- Concrete implementations (Agents, Environments, Models) MUST adhere strictly to their respective
  protocols without leaking implementation-specific requirements into caller logic.
- Entry points in `minisweagent/run` serve as composition roots responsible for selecting exactly
  one Agent, Environment, and Model for a given workflow.
- Rationale: Loose coupling through lightweight Python protocols allows seamless addition of new
  models, execution backends, and agent strategies without modifying existing core logic.

### III. Test-Driven Non-Mocking Integrity
Testing MUST validate real system behavior under authentic execution conditions.
- Test suites MUST use `pytest` exclusively; `unittest` conventions are prohibited.
- Tests MUST NOT mock or patch components unless explicitly authorized by user specification.
- Tests MUST be substantive; trivial assertion tests are prohibited, and every test MUST cover at
  least one demonstrable point of failure.
- Assertions MUST be direct and single-line (e.g., `assert func() == b`).
- Parameterized tests MUST format the first argument of `pytest.mark.parametrize` as a tuple and
  the second argument as a list.
- Rationale: Artificial mocks diverge from actual tool execution and shell behavior, compromising
  confidence in real agent trajectories.

### IV. Environment Isolation & Execution Safety
All agent interactions with target codebases MUST occur within clearly bounded execution environments.
- Environments (Local, Docker, Singularity) MUST manage process lifecycles, timeouts, and signal
  handling safely.
- Command execution MUST preserve environment state predictability and handle cleanup upon exit.
- File operations MUST remain scoped to designated workspace boundaries.
- Rationale: Autonomous agents running shell commands require strict containment to prevent host
  system corruption and ensure reproducible execution benchmarks.

### V. Fail-Fast & Transparent Error Propagation
Software defects and contract violations MUST surface immediately rather than being masked.
- Code MUST NOT catch exceptions unless explicitly instructed or required by protocol definition.
- Blanket exception catching (`except Exception: pass`) is strictly prohibited.
- Exceptions serve as informative diagnostics for users and agent loops to inspect failure modes.
- Rationale: Suppressing errors conceals critical failures, causing agent loops to hallucinate or
  loop indefinitely instead of resolving root causes.

## Technology Stack & Implementation Standards

The project codebase MUST strictly conform to modern Python standards:
- Target runtime MUST be Python 3.10 or higher.
- Native Python type annotations MUST be used throughout (e.g., `list` rather than `typing.List`).
- File system interactions MUST use `pathlib.Path` (e.g., `Path.read_text()` over `open()`).
- CLI commands and interfaces MUST be constructed using `typer`.
- Template formatting MUST use `jinja2`.
- Configuration state and specifications MUST be encapsulated within `@dataclass` structures.
- Commit messages MUST adhere to standard component tags: `fix`, `feat`, `enh`, `ref`, `docs`, `ci`,
  `dev`, or `chore`, scoped by component (`models`, `agents`, `env`, `config`, `run`, `benchmarks`,
  `cli`, `deps`).

## Analysis & Quality Verification Workflow

Analytical and exploratory workflows within this repository MUST maintain evidence-based rigor:
- Analysis phases MUST be strictly read-only; source code modification is prohibited during analysis.
- Every architectural or behavioral claim MUST be backed by code citations in `path:line` format.
- Claims MUST explicitly distinguish between verified facts and inferences using `[Verified]` and
  `[Inferred]` markers.
- Analysis outcomes MUST be cumulatively documented under `docs/analysis/`.
- Code reviews MUST prioritize identifying unhandled exceptions, logical inconsistencies, and
  breaking changes to interfaces over minor stylistic variations.

## Governance

This constitution serves as the foundational technical standard for the mini-SWE-agent project.
- The constitution supersedes ad-hoc coding patterns and unratified conventions.
- All code contributions, agent tasks, and pull requests MUST be reviewed for compliance with its
  core principles.
- Amendments MUST follow semantic versioning:
  - MAJOR: Incompatible governance alterations, principle removals, or core architecture redesigns.
  - MINOR: Addition of new principles, standards sections, or material scope expansions.
  - PATCH: Clarifications, documentation alignments, or non-semantic wording adjustments.
- Amendments require explicit documentation of rationale and an updated Sync Impact Report.

**Version**: 1.0.0 | **Ratified**: 2026-10-13 | **Last Amended**: 2026-10-13
