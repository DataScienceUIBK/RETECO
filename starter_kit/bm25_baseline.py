#!/usr/bin/env python3
"""RETECO BM25 starter baseline -- produces a TREC run file for one domain.

TRACK 1 (per query, and per step for Sub-Track 1b):
    python bm25_baseline.py --track 1 \
        --corpus documents.jsonl --queries examples.jsonl --out run.txt
    # step-level run for Sub-Track 1b:
    python bm25_baseline.py --track 1 --level step \
        --corpus documents.jsonl --queries steps.jsonl --out run_steps.txt

TRACK 2 (per turn; --strategy chooses how conversation context enters the query):
    python bm25_baseline.py --track 2 --strategy current \
        --corpus earthscience_documents.jsonl --queries earthscience_benchmark.json --out run.txt
    python bm25_baseline.py --track 2 --strategy history ...   # prepend conversation history

Output:  qid  Q0  docid  rank  score  bm25
"""
import argparse
import json

from bm25 import BM25


def read_jsonl(path):
    with open(path) as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def load_corpus(path, key):
    docs = read_jsonl(path)
    return [d[key] for d in docs], [d["content"] for d in docs]


def write_run(out, rows, tag="bm25"):
    with open(out, "w") as f:
        for qid, ranked in rows:
            for rank, (docid, score) in enumerate(ranked, 1):
                f.write(f"{qid}\tQ0\t{docid}\t{rank}\t{score:.6f}\t{tag}\n")


def track1_queries(path, level):
    items = read_jsonl(path)
    if level == "step":
        # steps_*.jsonl holds one record per query with its steps nested.
        # Official TEMPO run_step.py format: base query, blank line, "Step: <text>"
        return [(st["step_id"],
                 f'{it["query"]}\n\nStep: {st.get("step_instruction", "")}')
                for it in items for st in it.get("steps", [])]
    return [(it["id"], it["query"]) for it in items]


def track2_queries(path, strategy):
    bench = json.load(open(path))
    conv = [bench] if isinstance(bench, dict) else bench
    out = []
    for c in conv:
        for t in c["turns"]:
            qid = f"{c['id']}_turn_{t['turn_id']}"
            if strategy == "history":
                hist = t.get("conversation_history", "")
                if hist.lower().startswith("no previous"):
                    hist = ""
                q = (hist + " " + t["query"]).strip()
            else:  # current
                q = t["query"]
            out.append((qid, q))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--track", type=int, choices=[1, 2], required=True)
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--queries", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--level", choices=["query", "step"], default="query")
    ap.add_argument("--strategy", choices=["current", "history"], default="current")
    ap.add_argument("--top-k", type=int, default=100)
    ap.add_argument("--k1", type=float, default=0.9)
    ap.add_argument("--b", type=float, default=0.4)
    args = ap.parse_args()

    corpus_key = "id" if args.track == 1 else "doc_id"
    doc_ids, doc_texts = load_corpus(args.corpus, corpus_key)
    bm25 = BM25(doc_ids, doc_texts, k1=args.k1, b=args.b)

    if args.track == 1:
        queries = track1_queries(args.queries, args.level)
    else:
        queries = track2_queries(args.queries, args.strategy)

    rows = [(qid, bm25.search(q, args.top_k)) for qid, q in queries]
    write_run(args.out, rows)
    print(f"wrote {args.out}: {len(rows)} topics over {len(doc_ids)} docs "
          f"(track {args.track}, {args.level}/{args.strategy})")


if __name__ == "__main__":
    main()
