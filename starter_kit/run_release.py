#!/usr/bin/env python3
"""Driver: run the BM25 starter baseline over the RETECO release layout and score it.

Unlike run_all.py (which targets the pilot tree), this reads the train/dev
release produced by build_release.py.

Usage:
    python run_release.py --data ../reteco_data --split dev              # everything
    python run_release.py --data ../reteco_data --split dev \
        --track1 iota law --track2 drones                                # selected domains
"""
import argparse
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def sh(script, *args):
    subprocess.run([sys.executable, os.path.join(HERE, script), *args],
                   check=True, cwd=HERE, stdout=subprocess.DEVNULL)


def score(track, run, qrels, steps=None):
    cmd = [sys.executable, os.path.join(HERE, "scorer.py"), "--track", str(track),
           "--run", run, "--qrels", qrels, "--json"]
    if steps:
        cmd += ["--steps", steps]
    return json.loads(subprocess.run(cmd, capture_output=True, text=True,
                                     check=True).stdout)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=os.path.join(HERE, "..", "reteco_data"))
    ap.add_argument("--out", default=os.path.join(HERE, "runs_release"))
    ap.add_argument("--split", choices=["train", "dev"], default="dev")
    ap.add_argument("--track1", nargs="*", help="domain names (default: all)")
    ap.add_argument("--track2", nargs="*", help="domain names (default: all)")
    ap.add_argument("--top-k", type=int, default=100)
    args = ap.parse_args()

    data = os.path.abspath(args.data)
    runs = os.path.abspath(args.out)
    sp = args.split
    results = {"split": sp, "track1_tempo": {}, "track2_recor": {}}

    t1_root = os.path.join(data, "track1_tempo")
    doms1 = args.track1 if args.track1 is not None else sorted(os.listdir(t1_root))
    for dom in doms1:
        d = os.path.join(t1_root, dom)
        os.makedirs(os.path.join(runs, "track1", dom), exist_ok=True)
        entry = {}
        # 1a: whole-query retrieval
        run = os.path.join(runs, "track1", dom, f"1a_{sp}.txt")
        sh("bm25_baseline.py", "--track", "1", "--top-k", str(args.top_k),
           "--corpus", f"{d}/documents.jsonl",
           "--queries", f"{d}/examples_{sp}.jsonl", "--out", run)
        entry["1a"] = score(1, run, f"{d}/qrels_{sp}.txt",
                            steps=f"{d}/steps_{sp}.jsonl")
        # 1b: step-wise retrieval
        run = os.path.join(runs, "track1", dom, f"1b_{sp}.txt")
        sh("bm25_baseline.py", "--track", "1", "--level", "step",
           "--top-k", str(args.top_k), "--corpus", f"{d}/documents.jsonl",
           "--queries", f"{d}/steps_{sp}.jsonl", "--out", run)
        entry["1b"] = score(1, run, f"{d}/qrels_steps_{sp}.txt")
        results["track1_tempo"][dom] = entry
        print(f"track1/{dom:<10} 1a nDCG@10 {entry['1a']['nDCG@10']:.4f}   "
              f"1b nDCG@10 {entry['1b']['nDCG@10']:.4f}", flush=True)

    t2_root = os.path.join(data, "track2_recor")
    doms2 = args.track2 if args.track2 is not None else sorted(os.listdir(t2_root))
    for dom in doms2:
        d = os.path.join(t2_root, dom)
        os.makedirs(os.path.join(runs, "track2", dom), exist_ok=True)
        entry = {}
        for strategy in ("current", "history"):
            run = os.path.join(runs, "track2", dom, f"2a_{strategy}_{sp}.txt")
            sh("bm25_baseline.py", "--track", "2", "--strategy", strategy,
               "--top-k", str(args.top_k), "--corpus", f"{d}/documents.jsonl",
               "--queries", f"{d}/benchmark_{sp}.json", "--out", run)
            entry[strategy] = score(2, run, f"{d}/qrels_{sp}.txt")
        results["track2_recor"][dom] = entry
        print(f"track2/{dom:<18} 2a current {entry['current']['nDCG@10']:.4f}   "
              f"history {entry['history']['nDCG@10']:.4f}", flush=True)

    os.makedirs(runs, exist_ok=True)
    path = os.path.join(runs, f"baseline_{sp}.json")
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
