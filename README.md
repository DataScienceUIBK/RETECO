# RETECO — Reasoning-Oriented Retrieval

[Website](https://datascienceuibk.github.io/RETECO/) ·
[Task](https://datascienceuibk.github.io/RETECO/task.html) ·
[Data & Corpora](https://datascienceuibk.github.io/RETECO/data.html) ·
[Sample Data](https://datascienceuibk.github.io/RETECO/samples.html) ·
[Evaluation](https://datascienceuibk.github.io/RETECO/evaluation.html) ·
[Papers](https://datascienceuibk.github.io/RETECO/papers.html) ·
[Participate](https://datascienceuibk.github.io/RETECO/participate.html)

**RETECO** is a SemEval-2027 shared task on retrieval that must reason over
temporal constraints and multi-turn conversational context. It asks whether
retrieval and RAG systems can identify evidence that is relevant because of
*when* it applies and *what the conversation has already established*.

> RETECO has been accepted as a SemEval-2027 shared task.

[Read the final task proposal](docs/assets/papers/RETECO_SemEval_2027_Proposal.pdf)

## Tracks

| Track | Sub-track | Required output | Official retrieval score |
| --- | --- | --- | --- |
| 1 · Temporal Grounded Retrieval | 1a Temporal Retrieval | Ranked documents per query | nDCG@10 |
| 1 · Temporal Grounded Retrieval | 1b Step-wise Retrieval | Ranked documents per supplied step | Step-level nDCG@10 |
| 2 · Conversational Retrieval | 2a Conversational Retrieval | Ranked passages per target turn | nDCG@10 |
| 2 · Conversational Retrieval | 2b Gold-Passage Generation | Grounded answer | Five generation dimensions |
| 2 · Conversational Retrieval | 2c Full Conversational RAG | Ranked passages + grounded answer | nDCG@10; generation reported alongside |

See the [full task definitions](https://datascienceuibk.github.io/RETECO/task.html)
and [evaluation plan](https://datascienceuibk.github.io/RETECO/evaluation.html).

## Sample data

The repository contains a compact, human-inspected package copied from the
official TEMPO and RECOR releases:

- Track 1: 5 TEMPO examples, 26 supporting passages, and 26 positive qrels.
- Track 2: 4 RECOR conversations containing 13 turns, 15 supporting passages,
  and 32 positive qrels.
- A manifest pins the source dataset revisions and selected record IDs.

[Inspect samples online](https://datascienceuibk.github.io/RETECO/samples.html) ·
[Download the ZIP](https://datascienceuibk.github.io/RETECO/assets/downloads/RETECO_curated_sample_data.zip) ·
[Browse source files](docs/sample_data/)

The sample is a format and feasibility demonstration—not a new benchmark split
and not the hidden SemEval test set. It contains only referenced positive
evidence, so retrieval systems must not be evaluated against the sample corpus
alone.

## Data and corpora

### Track 1: TEMPO

[TEMPO](https://github.com/tempo-bench/Tempo) contains 1,730 complex temporal
queries, 3,976 decomposed retrieval steps, and 1,654,055 documents across 13
independent domain corpora.

| Group | Domain | Queries | Corpus documents |
| --- | --- | ---: | ---: |
| Blockchain | Bitcoin | 100 | 153,291 |
| Blockchain | Cardano | 51 | 87,201 |
| Blockchain | IOTA | 10 | 10,372 |
| Blockchain | Monero | 65 | 85,093 |
| Social Sciences | Economics | 83 | 93,756 |
| Social Sciences | Law | 35 | 43,288 |
| Social Sciences | Politics | 150 | 183,394 |
| Social Sciences | History | 801 | 356,493 |
| Applied | Quantitative Finance | 34 | 28,785 |
| Applied | Travel | 100 | 177,677 |
| Applied | Workplace | 36 | 64,659 |
| Applied | Genealogy | 115 | 156,228 |
| STEM | History of Science and Mathematics | 150 | 213,818 |
| **Total** | **13 domains** | **1,730** | **1,654,055** |

- Dataset: [tempo26/Tempo on Hugging Face](https://huggingface.co/datasets/tempo26/Tempo)
- Code and baselines: [tempo-bench/Tempo](https://github.com/tempo-bench/Tempo)
- Paper: [arXiv:2601.09523](https://arxiv.org/abs/2601.09523)

### Track 2: RECOR

[RECOR](https://github.com/RECOR-Benchmark/RECOR) contains 707 conversations,
2,971 target turns, and 507,141 documents across 11 domain corpora. Six domains
come from BRIGHT and five from StackExchange.

| Source | Domain | Conversations | Turns | Corpus documents |
| --- | --- | ---: | ---: | ---: |
| BRIGHT | Biology | 85 | 362 | 57,359 |
| BRIGHT | Earth Science | 98 | 454 | 121,249 |
| BRIGHT | Economics | 74 | 288 | 50,220 |
| BRIGHT | Psychology | 84 | 333 | 52,835 |
| BRIGHT | Robotics | 68 | 259 | 61,961 |
| BRIGHT | Sustainable Living | 78 | 319 | 60,792 |
| StackExchange | Drones | 37 | 142 | 16,381 |
| StackExchange | Hardware | 46 | 188 | 26,308 |
| StackExchange | Law | 50 | 230 | 20,027 |
| StackExchange | Medical Sciences | 44 | 183 | 23,297 |
| StackExchange | Politics | 43 | 213 | 16,712 |
| **Total** | **11 domains** | **707** | **2,971** | **507,141** |

- Dataset: [RECOR-Benchmark/RECOR on Hugging Face](https://huggingface.co/datasets/RECOR-Benchmark/RECOR)
- Code and baselines: [RECOR-Benchmark/RECOR](https://github.com/RECOR-Benchmark/RECOR)
- Published paper: [ACL Anthology 2026.findings-acl.129](https://aclanthology.org/2026.findings-acl.129/)

The public benchmarks support training and development. Final SemEval scoring
uses a separate, never-publicly-released test set with private gold judgments.

## Papers

### TEMPO

**TEMPO: A Realistic Multi-Domain Benchmark for Temporal Reasoning-Intensive
Retrieval**  
Abdelrahman Abdallah, Mohammed Ali, Muhammad Abdul-Mageed, and Adam Jatowt.  
arXiv:2601.09523, 2026. [Paper](https://arxiv.org/abs/2601.09523)

```bibtex
@article{abdallah2026tempo,
  title={TEMPO: A Realistic Multi-Domain Benchmark for Temporal Reasoning-Intensive Retrieval},
  author={Abdallah, Abdelrahman and Ali, Mohammed and Abdul-Mageed, Muhammad and Jatowt, Adam},
  journal={arXiv preprint arXiv:2601.09523},
  year={2026},
  url={https://arxiv.org/abs/2601.09523}
}
```

### RECOR

**RECOR: Reasoning-focused Multi-turn Conversational Retrieval Benchmark**  
Mohammed Ali, Abdelrahman Abdallah, Amit Agarwal, Hitesh Laxmichand Patel, and
Adam Jatowt.  
Findings of ACL 2026, pages 2688–2723.
[Paper](https://aclanthology.org/2026.findings-acl.129/) ·
[DOI](https://doi.org/10.18653/v1/2026.findings-acl.129)

```bibtex
@inproceedings{ali2026recor,
  title={RECOR: Reasoning-focused Multi-turn Conversational Retrieval Benchmark},
  author={Ali, Mohammed and Abdallah, Abdelrahman and Agarwal, Amit and Patel, Hitesh Laxmichand and Jatowt, Adam},
  booktitle={Findings of the Association for Computational Linguistics: ACL 2026},
  pages={2688--2723},
  year={2026},
  publisher={Association for Computational Linguistics},
  doi={10.18653/v1/2026.findings-acl.129},
  url={https://aclanthology.org/2026.findings-acl.129/}
}
```

Both records are available in [CITATIONS.bib](CITATIONS.bib). The official
RETECO task-paper citation will be added after the SemEval-2027 task description
is published.

## Repository map

```text
RETECO/
├── docs/                         # GitHub Pages website
│   ├── index.html
│   ├── task.html
│   ├── data.html                 # Detailed per-domain corpora
│   ├── samples.html              # Human-readable examples
│   ├── evaluation.html
│   ├── papers.html               # Proposal, papers, citations
│   ├── participate.html
│   ├── timeline.html
│   ├── sample_data/              # Curated machine-readable sample
│   └── assets/
│       ├── downloads/
│       └── papers/
├── .github/workflows/            # Pages deployment
├── CITATIONS.bib
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── README.md
```

Competition format checkers, local scorers, starter baselines, and sample
submissions will be added when their SemEval interfaces are frozen.

## Local website preview

The website is dependency-free:

```bash
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`.

## GitHub Pages deployment

The included workflow publishes `docs/`. In repository settings, choose
**GitHub Actions** as the Pages source. The site URL is:

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

## License

The SemEval data release is planned under CC BY 4.0. Existing benchmark data
and code may use different licenses; consult the license attached to each
resource. A repository-level software license will be added before the first
RETECO code release.
