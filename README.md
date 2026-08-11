# RETECO — Reasoning-Oriented Retrieval

[Website](https://datascienceuibk.github.io/RETECO/) · [Task](https://datascienceuibk.github.io/RETECO/task.html) · [Data](https://datascienceuibk.github.io/RETECO/data.html) · [Evaluation](https://datascienceuibk.github.io/RETECO/evaluation.html) · [Participate](https://datascienceuibk.github.io/RETECO/participate.html)

**RETECO** is a SemEval-2027 shared task on retrieval that must reason over
temporal constraints and multi-turn conversational context.

## Tracks

| Track | Sub-track | System output | Official retrieval score |
| --- | --- | --- | --- |
| 1 · Temporal Grounded Retrieval | 1a Temporal Retrieval | Ranked documents per query | nDCG@10 |
| 1 · Temporal Grounded Retrieval | 1b Step-wise Retrieval | Ranked documents per supplied step | Step-level nDCG@10 |
| 2 · Conversational Retrieval | 2a Conversational Retrieval | Ranked passages per target turn | nDCG@10 |
| 2 · Conversational Retrieval | 2b Gold-Passage Generation | Grounded answer | Five generation dimensions |
| 2 · Conversational Retrieval | 2c Full Conversational RAG | Ranked passages + grounded answer | nDCG@10; generation reported alongside |

## Public benchmark foundations

- [TEMPO](https://github.com/tempo-bench/Tempo): 1,730 complex temporal
  queries, 3,976 decomposed steps, 1,654,055 documents, and 13 domains.
- [RECOR](https://github.com/RECOR-Benchmark/RECOR): 707 conversations,
  2,971 turns, and 11 domains.

The public resources support training and development. SemEval evaluation uses
a separate held-out test set with private gold judgments.

## Repository map

```text
RETECO/
├── docs/                    # GitHub Pages website
│   ├── index.html
│   ├── task.html
│   ├── data.html
│   ├── evaluation.html
│   ├── participate.html
│   ├── timeline.html
│   └── assets/
├── .github/workflows/       # Pages deployment
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── README.md
```

Competition packages, format checkers, local scorers, starter baselines, and
sample submissions will be added as their interfaces are frozen.

## Local website preview

The site is dependency-free. From the repository root:

```bash
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`.

## GitHub Pages deployment

The included workflow publishes `docs/` to GitHub Pages. In the repository
settings, select **GitHub Actions** as the Pages source. The resulting project
URL is:

```text
https://datascienceuibk.github.io/RETECO/
```

## Important dates

- Sample data: August 8, 2026
- Training data: September 1, 2026
- Evaluation: January 10–31, 2027
- Paper and workshop dates: tentative; see the
  [official SemEval-2027 calendar](https://semeval.github.io/SemEval2027/)

## Organizers

Abdelrahman Abdallah, Mohammed Ali, Muhammad Abdul-Mageed, Kevin Duh, and
Adam Jatowt.

For task questions, contact
[Abdelrahman Abdallah](mailto:abdelrahman.abdallah@uibk.ac.at).

## Citation

The RETECO task citation will be added after publication of the SemEval task
description. Until then, cite the underlying TEMPO and RECOR benchmark papers;
BibTeX is available in their repositories.

## License

The SemEval data release is planned under CC BY 4.0. Individual source-code and
public benchmark repositories may use different licenses; consult the license
shipped with each resource. A repository-level software license will be added
before the first code release.
