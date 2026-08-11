# RETECO curated pilot data

This folder is a compact, human-inspected evidence subset copied from the
official **TEMPO** and **RECOR** releases. It demonstrates that both proposed
tracks have operational data formats, queries/conversations, complete positive
evidence sets, and machine-readable qrels.

## Important scope

- This is **pilot/trial material**, not a new benchmark split and not the hidden
  SemEval-2027 test set.
- The selection is deliberately diverse and easy to inspect; it is not claimed
  to be statistically representative or domain-balanced.
- Every referenced positive document is included. No synthetic negatives,
  relevance labels, queries, answers, or conversation turns were added.
- The included document collection is only an evidence subset. Retrieval
  baselines and official scoring must use the full track corpus, not rank only
  these positive documents.
- All records are in English.

## Contents

### `track1_tempo/`

- `examples.jsonl`: 5 complete temporal-retrieval examples.
- `steps.jsonl`: the matching official TEMPO step records.
- `documents.jsonl`: all 26 distinct gold passages referenced by the examples.
- `qrels.txt`: 26 positive query-document judgments in TREC format.

### `track2_recor/`

- `benchmark.jsonl`: 4 complete conversational records containing 13 turns.
- `documents.jsonl`: all 15 distinct passages referenced by those turns.
- `qrels.txt`: 32 positive turn-document judgments in TREC format. Query IDs use
  `<conversation_id>#turn<turn_id>`.

### Root files

- `manifest.json`: counts, selected IDs, source URLs, and pinned revisions.


