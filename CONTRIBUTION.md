# Contribution Guide

Thanks for helping expand the Data Engineering Practice Problems collection. This project thrives on a steady flow of realistic scenarios, clean reference implementations, and thoughtful documentation. Please use the guidance below to keep the repository approachable and consistent.

## Ways to Contribute

- **New practice problems** – add interview-style prompts, sample datasets, and reference solutions.
- **Enhance existing solutions** – improve performance, readability, resilience, or validation coverage.
- **Improve documentation** – clarify instructions, add diagrams or walkthroughs, fix typos.
- **Quality assurance** – add tests, linting, or automation that strengthens the developer experience.

## Contribution Workflow

1. **Discuss (optional but encouraged):** Open a draft issue describing the idea, especially for larger additions (new problem families, major refactors).
2. **Fork & branch:** Use feature branches named `feature/<summary>` or `fix/<summary>`.
3. **Develop locally:** Target Python 3.10+, prefer type hints, and keep third-party dependencies minimal. Include lightweight tests (`pytest`, doctest, or script-based checks) when feasible.
4. **Keep commits focused:** Each commit should represent a cohesive change with a clear message.
5. **Open a pull request:** Summarise what changed, why it matters, and how you validated it. Link related issues if applicable.

## Repository Structure Standards

- Each problem lives in its own folder at the repository root, e.g. `Problem X: <Descriptive Title>/`.
- Inside each problem directory:
  - `question.md` – prompt or requirements written in Markdown; include context, inputs, outputs, and any bonus objectives.
  - `solution.py` – reference implementation using standard library where possible; include a short module docstring explaining the approach.
  - Optional subdirectories (`data/`, `tests/`) if the problem demands bespoke assets. Keep paths relative (e.g., `../data/` for shared sample data).
- Shared datasets belong in the top-level `data/` directory. Provide a `README` snippet or inline comments describing their provenance if they are newly added.

## Problem Design Guidelines

- Aim for realistic data engineering themes: streaming ingestion, batch transformation, data quality, orchestration, storage optimisation, monitoring, or reliability.
- Calibrate difficulty with clear expectations. Outline assumptions, edge cases, and success criteria in `question.md`.
- When new problem types emerge (e.g., Airflow DAG design, dbt modelling), note the category at the top of the prompt for quick scanning.
- Prefer self-contained assets. If external services or APIs are referenced, provide mocks or clear instructions for local simulation.

## Coding & Documentation Standards

- Use descriptive naming, type hints, and concise comments where clarity is needed.
- For scripts, include a guarded `main()` entry point and friendly CLI output.
- Handle large-file scenarios with streaming reads/writes; avoid pulling entire datasets into memory unless the problem explicitly targets small inputs.
- Validate inputs defensively and surface actionable errors.
- If a contribution introduces dependencies, update any relevant setup instructions and pin versions in `requirements.txt` (create one if needed for the specific problem).

## Review Checklist

Before opening a pull request, confirm:

- [ ] `question.md` reads cleanly with correct Markdown formatting.
- [ ] `solution.py` runs locally using the provided instructions.
- [ ] New or modified datasets are documented and reasonably sized.
- [ ] Tests (if added) pass locally; include command snippets in the PR description.
- [ ] README references (if touched) remain accurate.

Thank you for sharing your expertise and helping fellow engineers level up. Star the repository to stay notified about new challenges and updates!
