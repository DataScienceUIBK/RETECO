<div align="center">

<img src="docs/assets/brand/reteco-mark.svg" alt="RETECO" width="88">

# RETECO

### A SemEval-2027 Shared Task on Reasoning-Oriented Retrieval

Retrieval that must reason about **when** evidence applies<br>
and **what the conversation has already established**.

[![SemEval-2027 Task 1](https://img.shields.io/badge/SemEval--2027-Task%201-07101d?style=for-the-badge)](https://semeval.github.io/SemEval2027/)
[![Dataset on Hugging Face](https://img.shields.io/badge/%F0%9F%A4%97%20Dataset-Available-5dd9ff?style=for-the-badge)](https://huggingface.co/datasets/DataScience-UIBK/RETECO-SemEval2027)
[![Website](https://img.shields.io/badge/Website-Live-1f6feb?style=for-the-badge)](https://datascienceuibk.github.io/RETECO/)

![Domains](https://img.shields.io/badge/domains-24-informational?style=flat-square)
![Documents](https://img.shields.io/badge/documents-2.16M-informational?style=flat-square)
![Split](https://img.shields.io/badge/train%2Fdev-70%2F30-informational?style=flat-square)
![Language](https://img.shields.io/badge/language-English-informational?style=flat-square)
![Text licence](https://img.shields.io/badge/text-CC%20BY--SA%204.0-brightgreen?style=flat-square)
![Annotation licence](https://img.shields.io/badge/annotations-CC%20BY%204.0-brightgreen?style=flat-square)

**[🌐 Website](https://datascienceuibk.github.io/RETECO/)** ·
**[📋 Task](https://datascienceuibk.github.io/RETECO/task.html)** ·
**[📊 Data](https://datascienceuibk.github.io/RETECO/data.html)** ·
**[🔍 Samples](https://datascienceuibk.github.io/RETECO/samples.html)** ·
**[📐 Evaluation](https://datascienceuibk.github.io/RETECO/evaluation.html)** ·
**[📄 Papers](https://datascienceuibk.github.io/RETECO/papers.html)** ·
**[🚀 Participate](https://datascienceuibk.github.io/RETECO/participate.html)**

[📕 Read the task proposal (PDF)](docs/assets/papers/RETECO_SemEval_2027_Proposal.pdf)

</div>

---

## 📰 News

| Date | | Update |
| :--- | :---: | :--- |
| **30 Aug 2026** | 🚀 | **Training and development data released.** All 24 domains, 2.16M documents, 70/30 train/dev splits with gold judgments for both — [get it on Hugging Face](https://huggingface.co/datasets/DataScience-UIBK/RETECO-SemEval2027). |
| **30 Aug 2026** | 🧰 | **Starter kit published.** BM25 baselines, the official `pytrec_eval` scorer, a submission format checker, and the deterministic build script — [`starter_kit/`](starter_kit/). |
| **30 Aug 2026** | 🧪 | **Reference baselines** for every retrieval sub-track on both splits — [`BASELINE_RESULTS.md`](starter_kit/BASELINE_RESULTS.md). |
| **11 Aug 2026** | ✅ | **RETECO accepted as SemEval-2027 Task 1** — [see the task list](https://semeval.github.io/SemEval2027/). |
| **08 Aug 2026** | 📦 | **Sample data published** — a compact, human-inspected package showing the exact record and submission formats. [Inspect the samples](https://datascienceuibk.github.io/RETECO/samples.html). |

> [!NOTE]
> **Next up:** registration, the participant mailing list, and the competition
> platform. They will be announced here and on the
> [participation guide](https://datascienceuibk.github.io/RETECO/participate.html).

---

## ⚡ Quick start

```bash
# 1 — get the data (~4.5 GB; everything you need, in one download)
pip install huggingface_hub
hf download DataScience-UIBK/RETECO-SemEval2027 --repo-type dataset --local-dir reteco_data

# 2 — get the baselines
git clone https://github.com/DataScienceUIBK/RETECO.git
cd RETECO/starter_kit && pip install -r requirements.txt

# 3 — develop on train, then check yourself on dev
python official_baseline.py --data ../../reteco_data --splits train
python official_baseline.py --data ../../reteco_data --splits dev
```

New to the task? The [participation guide](https://datascienceuibk.github.io/RETECO/participate.html)
walks through choosing a sub-track, building a system, and scoring it locally
with the same metric the leaderboard uses.

## 🎯 Tracks

| Track | Sub-track | Required output | Official retrieval score |
| --- | --- | --- | --- |
| 1 · Temporal Grounded Retrieval | 1a Temporal Retrieval | Ranked documents per query | nDCG@10 |
| 1 · Temporal Grounded Retrieval | 1b Step-wise Retrieval | Ranked documents per supplied step | Step-level nDCG@10 |
| 2 · Conversational Retrieval | 2a Conversational Retrieval | Ranked passages per target turn | nDCG@10 |
| 2 · Conversational Retrieval | 2b Gold-Passage Generation | Grounded answer | Five generation dimensions |
| 2 · Conversational Retrieval | 2c Full Conversational RAG | Ranked passages + grounded answer | nDCG@10; generation reported alongside |

See the [full task definitions](https://datascienceuibk.github.io/RETECO/task.html)
and [evaluation plan](https://datascienceuibk.github.io/RETECO/evaluation.html).

## 📊 Training and development data

The official train/dev release is on Hugging Face:
**[DataScience-UIBK/RETECO-SemEval2027](https://huggingface.co/datasets/DataScience-UIBK/RETECO-SemEval2027)**

```bash
hf download DataScience-UIBK/RETECO-SemEval2027 --repo-type dataset --local-dir reteco_data
```

One download contains everything needed for any sub-track: the full retrieval
corpus of all 24 domains, task files, and TREC qrels for both splits.

| | train | dev |
| --- | ---: | ---: |
| Track 1 queries | 1,211 | 519 |
| Track 1 steps | 2,762 | 1,214 |
| Track 2 conversations | 496 | 211 |
| Track 2 turns | 2,113 | 858 |

The split is 70/30 per domain with a fixed seed. The corpus is never split;
Track 1 splits on the query (steps are nested inside their query record) and
Track 2 splits on the whole conversation. Gold judgments ship for both splits —
the SemEval test set is separate and never released.

### 🧰 Starter kit

[`starter_kit/`](starter_kit/) has the baselines, scorer, format checker, and the
build script that produces the release from pinned upstream revisions.

```bash
cd starter_kit && pip install -r requirements.txt
python official_baseline.py --data ../../reteco_data --splits train dev
```

Reference BM25, nDCG@10, macro-averaged over domains:

| Sub-track | Query given to the retriever | train | dev |
| --- | --- | ---: | ---: |
| 1a Temporal retrieval | Whole query | 0.0879 | 0.0967 |
| 1b Step-wise retrieval | Query + step instruction | 0.0852 | 0.1063 |
| 2a Conversational retrieval | Current turn only | 0.1837 | 0.1827 |
| 2a Conversational retrieval | Turn + conversation history | 0.4539 | 0.4379 |

Per-domain numbers: [`starter_kit/BASELINE_RESULTS.md`](starter_kit/BASELINE_RESULTS.md).

## 🔍 Sample data

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

## 🗂️ Data and corpora

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

These are the upstream sources. The RETECO release above packages them into
train/dev splits with qrels. Final SemEval scoring uses a separate,
never-publicly-released test set with private gold judgments.

## 📄 Papers

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

## 🗺️ Repository map

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
├── starter_kit/                  # Baselines, scorer, format checker, build script
├── .github/workflows/            # Pages deployment
├── CITATIONS.bib
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
└── README.md
```

Format checkers, local scorers, and starter baselines are in
[`starter_kit/`](starter_kit/). Sample submissions will be added when the
competition-platform interface is frozen.

## 💻 Local website preview

The website is dependency-free:

```bash
python -m http.server 8000 --directory docs
```

Then open `http://localhost:8000/`.

## 🌐 GitHub Pages deployment

The included workflow publishes `docs/`. In repository settings, choose
**GitHub Actions** as the Pages source. The site URL is:

```text
https://datascienceuibk.github.io/RETECO/
```

## 📅 Important dates

- Sample data: August 8, 2026
- Training data: **released August 30, 2026**
- Evaluation: January 10–31, 2027
- Paper and workshop dates: tentative; see the
  [official SemEval-2027 calendar](https://semeval.github.io/SemEval2027/)

## 👥 Organizers

Abdelrahman Abdallah, Mohammed Ali, Muhammad Abdul-Mageed, Kevin Duh, and
Adam Jatowt.

For task questions, contact
[Abdelrahman Abdallah](mailto:abdelrahman.abdallah@uibk.ac.at).

## ⚖️ License

The data release carries two licenses. **Corpus and question/answer text is
CC BY-SA 4.0** — all passage text originates from Stack Exchange, whose user
contributions are licensed CC BY-SA, which is share-alike and cannot be
relicensed. **RETECO annotations (split assignments, TREC qrels,
`split_manifest.json`) are CC BY 4.0.** Attribution for the underlying content
remains with the original Stack Exchange authors.

Existing benchmark data and code may use different licenses; consult the license
attached to each resource. A repository-level software license will be added
before the first tagged RETECO code release.
