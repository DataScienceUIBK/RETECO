---
license: cc-by-sa-4.0
language:
  - en
task_categories:
  - text-retrieval
  - question-answering
tags:
  - semeval-2027
  - reasoning-retrieval
  - temporal-reasoning
  - conversational-retrieval
  - rag
pretty_name: RETECO SemEval-2027 Training and Development Data
size_categories:
  - 1M<n<10M
---

# RETECO — SemEval-2027 Task 1

Official **training and development data** for [RETECO](https://datascienceuibk.github.io/RETECO/),
the SemEval-2027 shared task on reasoning-oriented retrieval: retrieval that must
reason about *when* evidence applies and *what the conversation has already
established*.

| | |
| --- | --- |
| Task website | https://datascienceuibk.github.io/RETECO/ |
| Task definitions | https://datascienceuibk.github.io/RETECO/task.html |
| Evaluation plan | https://datascienceuibk.github.io/RETECO/evaluation.html |
| Code & baselines | https://github.com/DataScienceUIBK/RETECO |
| Contact | abdelrahman.abdallah@uibk.ac.at |

> **Not the SemEval test set.** This is train/dev only. Final SemEval scoring uses
> a separate, never-publicly-released test set with private gold judgments.

---

## What is in here

Two tracks, 24 independent domains, each domain self-contained with its own
retrieval corpus. Nothing needs to be fetched from anywhere else.

| | Domains | Corpus documents | Task items |
| --- | ---: | ---: | --- |
| **Track 1 · Temporal Grounded Retrieval** | 13 | 1,654,055 | 1,730 queries · 3,976 steps |
| **Track 2 · Conversational Retrieval** | 11 | 507,141 | 707 conversations · 2,971 turns |

The five RETECO sub-tracks draw on this data as follows:

| Sub-track | What you retrieve for | Files you need |
| --- | --- | --- |
| **1a** Temporal retrieval | one whole temporal query | `examples_*.jsonl` + `qrels_*.txt` |
| **1b** Step-wise retrieval | each decomposed step of a query | `steps_*.jsonl` + `qrels_steps_*.txt` |
| **2a** Conversational retrieval | each target turn of a conversation | `benchmark_*.json` + `qrels_*.txt` |
| **2b** Gold-passage generation | answer from supplied gold passages | `benchmark_*.json` |
| **2c** Full conversational RAG | retrieve **and** answer per turn | `benchmark_*.json` + `qrels_*.txt` |

---

## Splits: train / dev

Every domain is split **70 / 30** with a fixed seed (`20270101`). The exact
per-domain ID lists are in [`split_manifest.json`](split_manifest.json), so the
split is fully reproducible and auditable.

| | train | dev |
| --- | ---: | ---: |
| Track 1 queries | 1,211 | 519 |
| Track 1 steps | 2,762 | 1,214 |
| Track 2 conversations | 496 | 211 |
| Track 2 turns | 2,113 | 858 |

Three rules define the split:

1. **The corpus is never split.** `documents.jsonl` is the full domain corpus and
   is shared by train and dev — retrieval always runs against all documents of
   the domain, in both splits.
2. **Track 1 splits on the query.** A query's decomposed steps are nested *inside*
   its own record, so a step can never be separated from its query.
3. **Track 2 splits on the whole conversation.** Every turn of a conversation is
   in the same split, so no dialogue history leaks across the boundary.

Gold judgments are released for **both** splits. Use `train` to develop and
tune; use `dev` as your held-out check. The hidden SemEval test set is separate.

---

## Layout

```text
track1_tempo/<domain>/
  documents.jsonl              # full corpus, shared by both splits: {id, content}
  examples_train.jsonl         # 1a: {id, query, gold_ids, gold_answers}
  examples_dev.jsonl
  steps_train.jsonl            # 1b: one record per query, steps nested
  steps_dev.jsonl
  guidance_train.jsonl         # temporal metadata + gold passage annotations
  guidance_dev.jsonl
  qrels_train.txt              # 1a judgments  — TREC: qid 0 docid 1
  qrels_dev.txt
  qrels_steps_train.txt        # 1b judgments  — topic id = step_id
  qrels_steps_dev.txt

track2_recor/<domain>/
  documents.jsonl              # full corpus: {doc_id, content}
  benchmark_train.json         # conversations: turns, history, gold_doc_ids
  benchmark_dev.json
  qrels_train.txt              # 2a/2c judgments — qid = <conv_id>_turn_<turn_id>
  qrels_dev.txt

split_manifest.json            # seed, per-domain counts, exact ID lists, provenance
```

**Track 1 domains** — bitcoin, cardano, economics, genealogy, history, hsm, iota,
law, monero, politics, quant, travel, workplace.
**Track 2 domains** — biology, drones, earth_science, economics, hardware, law,
medicalsciences, politics, psychology, robotics, sustainable_living.

### Record formats

```jsonc
// track1_tempo/<domain>/examples_{train,dev}.jsonl        — Sub-track 1a
{"id": "124973_5", "query": "How long does Bitcoin Core store forked chains? ...",
 "gold_ids": ["bitcoin/45eff6bd_1297.txt", ...], "gold_answers": ["..."]}

// track1_tempo/<domain>/steps_{train,dev}.jsonl           — Sub-track 1b
{"id": "124973_5", "query": "How long does Bitcoin Core store forked chains? ...",
 "steps": [
   {"step_id": "124973_5_step1", "step": 1,
    "step_instruction": "Consult Bitcoin Core official documentation ...",
    "gold_ids": ["bitcoin/45eff6bd_1297.txt"]},
   {"step_id": "124973_5_step2", "step": 2, "...": "..."}]}

// track2_recor/<domain>/benchmark_{train,dev}.json        — Sub-tracks 2a/2b/2c
{"id": "ex_3025", "task": "drones", "original_query": "...", "original_answer": "...",
 "turns": [
   {"turn_id": 1, "query": "In FPV drone motors, why is lubrication only ...",
    "answer": "...", "conversation_history": "No previous conversation.",
    "subquestion_reasoning": "...", "gold_doc_ids": ["drones_ex_3025_doc_0", ...]}],
 "metadata": {"num_turns": 4, "gold_doc_count": 11, "source": "annotated_data"}}

// qrels — TREC 4-column, binary relevance, tab-separated
124973_5        0       bitcoin/45eff6bd_1297.txt       1
ex_3025_turn_1  0       drones_ex_3025_doc_0            1
```

**Topic IDs** (use these exact forms in submissions):
1a `id` · 1b `step_id` = `<query_id>_step<n>` · 2a/2c `<conversation_id>_turn_<turn_id>`

---

## How to use

### 1. Download

```bash
pip install huggingface_hub
hf download DataScience-UIBK/RETECO-SemEval2027 --repo-type dataset \
    --local-dir reteco_data
```

### 2. Get the baselines

```bash
git clone https://github.com/DataScienceUIBK/RETECO.git
cd RETECO/starter_kit
pip install -r requirements.txt          # pytrec_eval, gensim, pyserini (needs a JDK)
```

### 3. Run on **train**, then on **dev**

The runner takes `--splits`, so train and dev are the same command with one word
changed. Develop against `train`; keep `dev` as your held-out check.

```bash
export JAVA_HOME=/path/to/jdk
export JVM_PATH=$JAVA_HOME/lib/server/libjvm.so

# development split — tune here
python official_baseline.py --data ../../reteco_data --out ../../baselines \
    --splits train

# held-out split — check here
python official_baseline.py --data ../../reteco_data --out ../../baselines \
    --splits dev

# or both in one pass (corpus is indexed once and reused across splits)
python official_baseline.py --data ../../reteco_data --out ../../baselines \
    --splits train dev

# one domain, for a fast smoke test
python official_baseline.py --track1 iota --track2 drones --splits train dev
```

Each run writes, per domain, a TREC run file `run_<subtrack>_<split>.trec` and a
`results.json`; the top level gets a `summary.json` with per-domain and
macro-averaged metrics. Per-domain results are cached, so an interrupted run
resumes where it stopped.

### 4. Score your own run

nDCG@10 via `pytrec_eval` is the official RETECO metric.

```bash
python -c "
import pytrec_eval, json
qrels = {}
for ln in open('reteco_data/track1_tempo/iota/qrels_dev.txt'):
    q,_,d,r = ln.split(); qrels.setdefault(q,{})[d] = int(r)
run = {}
for ln in open('my_run.trec'):
    q,_,d,rank,score,_tag = ln.split(); run.setdefault(q,{})[d] = float(score)
ev = pytrec_eval.RelevanceEvaluator(qrels, {'ndcg_cut.10'})
s = ev.evaluate(run)
print('nDCG@10', sum(v['ndcg_cut_10'] for v in s.values())/len(s))
"
```

A dependency-free starter baseline and scorer (`bm25_baseline.py`, `scorer.py`)
are also in `starter_kit/` if you want to begin without installing a JDK.

---

## Reference baseline

BM25 on this release, macro-averaged over domains, nDCG@10. Retrieval and
scoring use the same implementation the upstream benchmarks use (Lucene analyzer
+ gensim `LuceneBM25Model`, k1=0.9 / b=0.4; `pytrec_eval` for metrics).

| Sub-track | train | dev |
| --- | ---: | ---: |
| 1a · whole-query retrieval | 0.0879 | 0.0967 |
| 1b · step-wise retrieval | 0.0852 | 0.1063 |
| 2a · current turn only | 0.1837 | 0.1827 |
| 2a · query + conversation history | 0.4539 | 0.4379 |

Two things to read off this table. Lexical matching alone is weak on Track 1 —
temporal grounding is not a keyword problem, and there is a lot of headroom.
And on Track 2, simply appending the conversation history lifts BM25 from 0.18
to 0.44, which is the size of the signal a conversational system has to exploit.

Per-domain numbers for both splits: `BASELINE_RESULTS.md` in the RETECO repo.

---

## Provenance

Built deterministically from pinned upstream revisions:

| Source | Dataset | Revision |
| --- | --- | --- |
| TEMPO | [`tempo26/Tempo`](https://huggingface.co/datasets/tempo26/Tempo) | `f9df06c05688225e37701974d23c8e3c5d4efaf6` |
| RECOR | [`RECOR-Benchmark/RECOR`](https://huggingface.co/datasets/RECOR-Benchmark/RECOR) | `d9faa639019dcfa1a1fea2aece55ebcba3083c00` |

Every published corpus, query, step, conversation and turn count reproduces
exactly. TEMPO's four LLM query-reformulation configs are **not** included: the
official system input is the original query. Three RECOR gold document IDs name
documents absent from every corpus; they are dropped from the qrels so a perfect
ranking stays attainable, and are listed per-domain in `split_manifest.json`.

---

## Licensing

Two licenses, because text and annotations have different origins:

- **Corpus and Q&A text — CC BY-SA 4.0.** All passage text originates from Stack
  Exchange (directly, or via [BRIGHT](https://huggingface.co/datasets/xlangai/BRIGHT)
  for six Track 2 domains). Stack Exchange contributions are CC BY-SA, which is
  share-alike: redistribution must preserve the license and attribution. The
  repository is labelled `cc-by-sa-4.0` for this reason.
- **RETECO annotations — CC BY 4.0.** Split assignments, TREC qrels and
  `split_manifest.json` are contributed by the RETECO organizers.

Attribution for the underlying content remains with the original Stack Exchange
authors. Do not redistribute hidden evaluation data or inferred gold labels.

---

## Citation

```bibtex
@article{abdallah2026tempo,
  title={TEMPO: A Realistic Multi-Domain Benchmark for Temporal Reasoning-Intensive Retrieval},
  author={Abdallah, Abdelrahman and Ali, Mohammed and Abdul-Mageed, Muhammad and Jatowt, Adam},
  journal={arXiv preprint arXiv:2601.09523}, year={2026},
  url={https://arxiv.org/abs/2601.09523}
}

@inproceedings{ali2026recor,
  title={RECOR: Reasoning-focused Multi-turn Conversational Retrieval Benchmark},
  author={Ali, Mohammed and Abdallah, Abdelrahman and Agarwal, Amit and Patel, Hitesh Laxmichand and Jatowt, Adam},
  booktitle={Findings of the Association for Computational Linguistics: ACL 2026},
  pages={2688--2723}, year={2026},
  publisher={Association for Computational Linguistics},
  doi={10.18653/v1/2026.findings-acl.129}
}
```

The RETECO task-description citation will be added once the SemEval-2027
proceedings are published.
