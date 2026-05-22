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

- Every problem lives in `problems/NNN-kebab-case-title/` where `NNN` is a zero-padded id (`001`, `065`, ...). Pick the next free id.
- Inside each problem directory:
  - `question.md` – the problem prompt. **Must start with YAML frontmatter** (see below), followed by a single H1 `# Problem N — Title`, then the body.
  - `solution.md` – written walkthrough (preferred for design / discussion problems), **or** `solution.py` for runnable code problems. Pick one; the frontmatter declares which.
  - Optional subdirectories (`data/`, `tests/`) if the problem demands bespoke assets. Keep paths relative (e.g., `../../data/` for shared sample data).
- Shared datasets belong in the top-level `data/` directory. Provide a `README` snippet or inline comments describing their provenance if they are newly added.

### Required frontmatter

Every `question.md` begins with this block — `PROBLEMS.md` is generated from it:

```yaml
---
id: 21
title: Data Platform for an Electricity Retailer
category: System Design
topics: [smart meter, IoT, warehouse, batch]
difficulty: Hard
solution: solution.md
---
```

Allowed `category` values match the legend in `PROBLEMS.md`. `difficulty` is one of `Easy`, `Medium`, `Hard`. `solution` is the filename of the answer file in the same folder.

### Regenerating the index

After adding or editing a problem, regenerate the top-level index:

```bash
python3 scripts/build_index.py
```

CI (or a pre-PR check) can verify staleness with:

```bash
python3 scripts/build_index.py --check
```

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

- [ ] `question.md` has valid frontmatter (id, title, category, topics, difficulty, solution).
- [ ] `question.md` reads cleanly with correct Markdown formatting.
- [ ] The declared `solution` file exists and is the right type (`.md` or `.py`).
- [ ] `python3 scripts/build_index.py --check` passes.
- [ ] README references (if touched) remain accurate.

Thank you for sharing your expertise and helping fellow engineers level up. Star the repository to stay notified about new challenges and updates!
