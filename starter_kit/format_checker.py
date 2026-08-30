#!/usr/bin/env python3
"""RETECO submission format checker.

Validates a run file in TREC format:

    qid   Q0   docid   rank   score   tag

Rules enforced (same as the CodaBench checker will use):
  * exactly 6 whitespace-separated columns per non-empty line
  * rank is a positive integer, score is a float
  * ranks within a topic are unique
  * (warn) scores within a topic are non-increasing with rank
  * (optional) --qrels restricts the valid topic ids and warns on unknown docids

Exit code 0 = valid, 1 = errors found.

Usage:
    python format_checker.py run.txt
    python format_checker.py run.txt --qrels qrels.txt --corpus documents.jsonl
"""
import argparse
import json
import sys


def load_ids(path, key):
    ids = set()
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                ids.add(json.loads(line)[key])
    return ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("--qrels", help="optional qrels.txt to validate topic ids")
    ap.add_argument("--corpus", help="optional documents.jsonl to validate doc ids")
    ap.add_argument("--doc-key", default="id", help="doc id field in corpus (id|doc_id)")
    args = ap.parse_args()

    valid_topics = None
    if args.qrels:
        valid_topics = set()
        with open(args.qrels) as f:
            for ln in f:
                if ln.strip():
                    valid_topics.add(ln.split()[0])
    valid_docs = load_ids(args.corpus, args.doc_key) if args.corpus else None

    errors, warnings = [], []
    per_topic_ranks, per_topic_last_score = {}, {}
    n = 0
    with open(args.run) as f:
        for lineno, raw in enumerate(f, 1):
            line = raw.strip()
            if not line:
                continue
            n += 1
            cols = line.split()
            if len(cols) != 6:
                errors.append(f"L{lineno}: expected 6 columns, got {len(cols)}")
                continue
            qid, q0, docid, rank, score, tag = cols
            try:
                rank = int(rank)
                assert rank > 0
            except Exception:
                errors.append(f"L{lineno}: rank must be a positive integer, got '{cols[3]}'")
            try:
                score = float(score)
            except Exception:
                errors.append(f"L{lineno}: score must be a float, got '{cols[4]}'")
                continue
            if valid_topics is not None and qid not in valid_topics:
                warnings.append(f"L{lineno}: topic '{qid}' not in qrels")
            if valid_docs is not None and docid not in valid_docs:
                warnings.append(f"L{lineno}: docid '{docid}' not in corpus")
            ranks = per_topic_ranks.setdefault(qid, set())
            if isinstance(rank, int):
                if rank in ranks:
                    errors.append(f"L{lineno}: duplicate rank {rank} in topic '{qid}'")
                ranks.add(rank)
            prev = per_topic_last_score.get(qid)
            if prev is not None and score > prev + 1e-9:
                warnings.append(f"L{lineno}: score increases with rank in topic '{qid}'")
            per_topic_last_score[qid] = score

    print(f"lines: {n}  topics: {len(per_topic_ranks)}  "
          f"errors: {len(errors)}  warnings: {len(warnings)}")
    for e in errors[:50]:
        print("  ERROR  ", e)
    for w in warnings[:20]:
        print("  warn   ", w)
    if errors:
        print("RESULT: INVALID")
        sys.exit(1)
    print("RESULT: VALID")


if __name__ == "__main__":
    main()
