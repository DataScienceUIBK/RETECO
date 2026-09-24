# RETECO starter kit

Reference code for SemEval-2027 Task 1. Two levels:

| | Dependencies | Use |
| --- | --- | --- |
| **Official baseline** (`official_baseline.py`) | pyserini + JDK, gensim, pytrec_eval | Reproduces the published RETECO baseline numbers |
| **Pure-Python starter** (`bm25_baseline.py` + `scorer.py`) | none | Zero-install starting point; approximate |

## Official baseline

Retrieval is the verbatim `retrieval_bm25` from the two upstream benchmark
repos, which ship byte-identical implementations:

- https://github.com/tempo-bench/Tempo — `retrievers.py`
- https://github.com/RECOR-Benchmark/RECOR — `experiments/retrieval/retrievers.py`

That is: the Lucene analyzer via pyserini, gensim `LuceneBM25Model` with
`k1=0.9, b=0.4`, top-1000 cut. Scoring is the upstream `calculate_retrieval_metrics`
— `pytrec_eval` with `ndcg_cut`, `map_cut`, `recall`, `P` and `recip_rank`.
**nDCG@10 from `pytrec_eval` is the official RETECO metric.**

Query construction follows upstream exactly:

| Sub-track | Query | Topic id |
| --- | --- | --- |
| 1a | `examples['query']` | `id` |
| 1b | `f"{base_query}\n\nStep: {step_instruction}"` | `step_id` |
| 2a | `turn['query']` (current turn only) | `{conversation_id}_turn_{turn_id}` |

```bash
export JAVA_HOME=/path/to/jdk
export JVM_PATH=$JAVA_HOME/lib/server/libjvm.so
python official_baseline.py --data ../reteco_data --out ../baselines_official \
    --splits train dev
# one domain only:
python official_baseline.py --track1 iota --track2 drones --splits dev
```

Per-domain `results.json` is cached, so the run is resumable. The corpus is
analysed and indexed once per domain and reused across splits — the only
deviation from upstream's per-invocation flow, and it changes wall clock only,
not scores.

## Pure-Python starter

No dependencies at all. Approximates the official setup (same `k1`/`b`, simpler
tokenisation) and adds RETECO's temporal and turn-depth diagnostics, which are
not part of the upstream retrieval metrics.

```bash
python run_release.py --data ../reteco_data --split dev --track1 iota --track2 drones
```

## Building the release from upstream

```bash
python download_raw.py                     # pinned TEMPO + RECOR snapshots
python build_release.py --raw ../hf_raw --out ../reteco_data_v1.0
python dedup_track1.py --src ../reteco_data_v1.0 --dst ../reteco_data       # data v1.1
python verify_dedup_track1.py --old ../reteco_data_v1.0 --new ../reteco_data
```

`build_release.py` is deterministic: same seed, same splits, and it re-verifies
every published count on each run. It produces data v1.0.

`dedup_track1.py` turns v1.0 into v1.1. In every Track 1 corpus it keeps one
copy of each text (identical ignoring whitespace), always keeping a gold ID
when a group of copies contains one, and renames removed IDs to the kept ID in
every task file. It writes `duplicate_map.json` (removed ID -> kept ID) per
domain. Track 2 is copied unchanged. `verify_dedup_track1.py` checks the result
against v1.0: no gold text lost, qrels and task files equal to v1.0 with IDs
mapped, Track 2 byte-identical.

## Format checker

`format_checker.py` validates a submission before you send it. Run it on every
run file — a submission that fails validation should never reach the
competition platform.
