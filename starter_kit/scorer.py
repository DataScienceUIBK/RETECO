#!/usr/bin/env python3
"""RETECO official scorer (pure Python, no dependencies).

Scores a TREC run file against qrels and reports the official metric plus the
track-specific diagnostics.

TRACK 1 (Temporal Grounded Retrieval):
    python scorer.py --track 1 --run run.txt --qrels qrels.txt [--steps steps.jsonl]
    -> nDCG@10 (official) + TP@10, TR@10, TC@10, NDCG|FC@10
       (TC / NDCG|FC require --steps, which defines the required time periods.)

TRACK 2 (Reasoning-Intensive Conversational Retrieval):
    python scorer.py --track 2 --run run.txt --qrels qrels.txt
    -> nDCG@10 (official) overall, plus a breakdown by turn position (T1..T5+).

Run file:  qid  Q0  docid  rank  score  tag
Qrels:     qid  0   docid  rel
"""
import argparse
import json
from collections import defaultdict

from ir_metrics import (ndcg_at_k, temporal_precision_at_k,
                        temporal_relevance_at_k, temporal_coverage_at_k, mean)


def load_qrels(path):
    gold = defaultdict(set)
    with open(path) as f:
        for ln in f:
            if not ln.strip():
                continue
            qid, _, docid, rel = ln.split()
            if int(rel) > 0:
                gold[qid].add(docid)
    return gold


def load_run(path):
    ranked = defaultdict(list)  # qid -> [(rank, score, docid)]
    with open(path) as f:
        for ln in f:
            if not ln.strip():
                continue
            qid, _, docid, rank, score, _tag = ln.split()
            ranked[qid].append((int(rank), float(score), docid))
    out = {}
    for qid, rows in ranked.items():
        rows.sort(key=lambda r: (r[0], -r[1]))
        out[qid] = [d for _, _, d in rows]
    return out


def load_steps(path):
    """qid -> list of gold-id sets (one per required period/step).

    steps_*.jsonl holds one record per query with its steps nested beneath it.
    """
    periods = defaultdict(list)
    with open(path) as f:
        for ln in f:
            if not ln.strip():
                continue
            rec = json.loads(ln)
            for st in rec.get("steps", []):
                periods[rec["id"]].append(set(st.get("gold_ids", [])))
    return periods


def turn_bucket(qid):
    """RECOR topic ids look like 'ex_3025_turn_3' -> bucket 'T3' (T5+ capped)."""
    if "_turn_" in qid:
        try:
            t = int(qid.rsplit("_turn_", 1)[1])
            return "T5+" if t >= 5 else f"T{t}"
        except ValueError:
            pass
    return "T?"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", type=int, choices=[1, 2], required=True)
    ap.add_argument("--run", required=True)
    ap.add_argument("--qrels", required=True)
    ap.add_argument("--steps", help="Track 1: steps.jsonl defining required periods")
    ap.add_argument("--k", type=int, default=10)
    ap.add_argument("--json", action="store_true", help="emit JSON instead of text")
    args = ap.parse_args()

    gold = load_qrels(args.qrels)
    run = load_run(args.run)
    k = args.k
    qids = [q for q in gold if q in run]

    result = {"k": k, "num_topics": len(qids)}

    if args.track == 1:
        periods = load_steps(args.steps) if args.steps else {}
        ndcgs, tps, trs, tcs, fc_ndcgs = [], [], [], [], []
        for q in qids:
            docs = run[q]
            nd = ndcg_at_k(docs, gold[q], k)
            ndcgs.append(nd)
            trs.append(temporal_relevance_at_k(docs, gold[q], k))
            tps.append(temporal_precision_at_k(docs, gold[q], k))
            tc = temporal_coverage_at_k(docs, periods.get(q, []), k)
            tcs.append(tc)
            if tc == 1.0:
                fc_ndcgs.append(nd)
        result.update({
            "nDCG@%d" % k: round(mean(ndcgs), 4),
            "TP@%d" % k: round(mean(tps), 4),
            "TR@%d" % k: round(mean(trs), 4),
            "TC@%d" % k: round(mean(tcs), 4),
            "NDCG|FC@%d" % k: round(mean(fc_ndcgs), 4),
            "num_full_coverage": sum(1 for t in tcs if t == 1.0),
        })
        official = "nDCG@%d" % k
    else:
        by_turn = defaultdict(list)
        allnd = []
        for q in qids:
            nd = ndcg_at_k(run[q], gold[q], k)
            allnd.append(nd)
            by_turn[turn_bucket(q)].append(nd)
        result["nDCG@%d" % k] = round(mean(allnd), 4)
        result["by_turn"] = {t: round(mean(v), 4) for t, v in sorted(by_turn.items())}
        official = "nDCG@%d" % k

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"# RETECO Track {args.track} -- {result['num_topics']} topics scored")
        for key, val in result.items():
            if key in ("k", "num_topics"):
                continue
            marker = "  <-- OFFICIAL" if key == official else ""
            print(f"  {key:14s} {val}{marker}")


if __name__ == "__main__":
    main()
