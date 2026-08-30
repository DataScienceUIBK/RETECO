#!/usr/bin/env python3
"""Build the unified RETECO SemEval-2027 train/dev release.

Reads the full TEMPO and RECOR snapshots downloaded by download_raw.py and
emits one self-contained tree: every domain carries its own corpus, its task
files split 70/30 into train and dev, and TREC qrels for both splits.

The split unit is the *query* (Track 1) and the *whole conversation* (Track 2).
Corpora are never split -- retrieval always runs against the full domain corpus.
Track 1b steps and the reformulation variants follow their parent query.

Usage:
    python build_release.py --raw ../hf_raw --out ../reteco_data
"""
import argparse
import ast
import gzip
import json
import os
import random
import shutil
from collections import OrderedDict

import numpy as np
import pyarrow.parquet as pq

SEED = 20270101
TRAIN_FRACTION = 0.70

TEMPO_PINS = ("tempo26/Tempo", "f9df06c05688225e37701974d23c8e3c5d4efaf6")
RECOR_PINS = ("RECOR-Benchmark/RECOR", "d9faa639019dcfa1a1fea2aece55ebcba3083c00")



# ---------------------------------------------------------------- helpers ---
def plain(v):
    """numpy/pandas -> json-serialisable python."""
    if isinstance(v, np.ndarray):
        return [plain(x) for x in v]
    if isinstance(v, (list, tuple)):
        return [plain(x) for x in v]
    if isinstance(v, dict):
        return {k: plain(x) for k, x in v.items()}
    if isinstance(v, np.generic):
        return v.item()
    return v


def gold_list(v):
    """TEMPO stores step gold_ids as a repr'd list string; queries store arrays."""
    if v is None:
        return []
    if isinstance(v, str):
        v = v.strip()
        if not v:
            return []
        try:
            return [str(x) for x in ast.literal_eval(v)]
        except (ValueError, SyntaxError):
            return []
    return [str(x) for x in plain(v)]


def write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    return len(records)


def write_qrels(path, pairs):
    """pairs: iterable of (qid, docid). Binary relevance, TREC 4-column."""
    n = 0
    with open(path, "w", encoding="utf-8") as f:
        for qid, docid in pairs:
            f.write(f"{qid}\t0\t{docid}\t1\n")
            n += 1
    return n


def split_ids(ids, seed_salt):
    """Deterministic 70/30 split over a sorted id list."""
    ids = sorted(ids)
    rng = random.Random(f"{SEED}:{seed_salt}")
    shuffled = ids[:]
    rng.shuffle(shuffled)
    n_train = max(1, round(len(shuffled) * TRAIN_FRACTION)) if len(shuffled) > 1 else len(shuffled)
    n_train = min(n_train, len(shuffled) - 1) if len(shuffled) > 1 else n_train
    return set(shuffled[:n_train]), set(shuffled[n_train:])


# ------------------------------------------------------------- track 1 -----
def build_tempo(raw, out, manifest, report):
    src = os.path.join(raw, "tempo")
    domains = sorted(f[:-8] for f in os.listdir(os.path.join(src, "examples"))
                     if f.endswith(".parquet"))
    for dom in domains:
        dst = os.path.join(out, "track1_tempo", dom)
        os.makedirs(dst, exist_ok=True)

        # ---- corpus (never split) -----------------------------------------
        corpus_ids = set()
        n_docs = 0
        with open(os.path.join(dst, "documents.jsonl"), "w", encoding="utf-8") as f:
            pf = pq.ParquetFile(os.path.join(src, "documents", f"{dom}.parquet"))
            for batch in pf.iter_batches(batch_size=5000, columns=["id", "content"]):
                for did, content in zip(batch.column("id").to_pylist(),
                                        batch.column("content").to_pylist()):
                    f.write(json.dumps({"id": did, "content": content},
                                       ensure_ascii=False) + "\n")
                    corpus_ids.add(did)
                    n_docs += 1

        # ---- queries -------------------------------------------------------
        ex = pq.read_table(os.path.join(src, "examples", f"{dom}.parquet")).to_pylist()
        by_qid = OrderedDict()
        for row in ex:
            by_qid[row["id"]] = {
                "id": row["id"],
                "query": row["query"],
                "gold_ids": gold_list(row.get("gold_ids")),
                "gold_answers": plain(row.get("gold_answers")) or [],
            }
        train_ids, dev_ids = split_ids(by_qid.keys(), f"tempo:{dom}")

        # ---- steps (Sub-track 1b) + temporal guidance -----------------------
        st = pq.read_table(os.path.join(src, "steps", f"{dom}.parquet")).to_pylist()
        step_records, guidance = [], []
        n_steps = 0
        for row in st:
            qid = row["id"]
            qg = plain(row.get("query_guidance")) or {}
            guidance.append({
                "id": qid,
                "query_guidance": qg,
                "gold_passage_annotations": plain(row.get("gold_passage_annotations")) or [],
            })
            steps = []
            for entry in qg.get("retrieval_plan") or []:
                gids = gold_list(entry.get("gold_ids"))
                if not gids:
                    continue  # unscoreable: no gold evidence for this step
                steps.append({
                    "step_id": f"{qid}_step{entry.get('step')}",
                    "step": entry.get("step"),
                    "step_instruction": entry.get("action", ""),
                    "gold_ids": gids,
                })
            if steps:
                # One record per query, mirroring the upstream layout: the query
                # text appears once and its steps are nested beneath it.
                step_records.append({
                    "id": qid,
                    "query": by_qid[qid]["query"] if qid in by_qid else row["query"],
                    "steps": steps,
                })
                n_steps += len(steps)

        # ---- emit splits ----------------------------------------------------
        counts = {}
        for split, keep in (("train", train_ids), ("dev", dev_ids)):
            qs = [q for qid, q in by_qid.items() if qid in keep]
            ss = [r for r in step_records if r["id"] in keep]
            gs = [g for g in guidance if g["id"] in keep]
            write_jsonl(os.path.join(dst, f"examples_{split}.jsonl"), qs)
            write_jsonl(os.path.join(dst, f"steps_{split}.jsonl"), ss)
            write_jsonl(os.path.join(dst, f"guidance_{split}.jsonl"), gs)
            nq = write_qrels(os.path.join(dst, f"qrels_{split}.txt"),
                             ((q["id"], d) for q in qs for d in q["gold_ids"]
                              if d in corpus_ids))
            ns = write_qrels(os.path.join(dst, f"qrels_steps_{split}.txt"),
                             ((st_["step_id"], d) for r in ss for st_ in r["steps"]
                              for d in st_["gold_ids"] if d in corpus_ids))
            counts[split] = {"queries": len(qs),
                             "steps": sum(len(r["steps"]) for r in ss),
                             "step_records": len(ss),
                             "qrels_query": nq, "qrels_step": ns}

        # ---- validation ------------------------------------------------------
        assert not (train_ids & dev_ids), f"{dom}: train/dev overlap"
        missing = {d for q in by_qid.values() for d in q["gold_ids"] if d not in corpus_ids}
        missing |= {d for r in step_records for st_ in r["steps"]
                    for d in st_["gold_ids"] if d not in corpus_ids}
        report["tempo_missing_gold"][dom] = sorted(missing)

        manifest["track1_tempo"][dom] = {
            "documents": n_docs,
            "dropped_gold_ids": sorted(missing),
            "queries_total": len(by_qid),
            "steps_total": n_steps,
            "step_records_total": len(step_records),
            "train": counts["train"], "dev": counts["dev"],
            "train_ids": sorted(train_ids), "dev_ids": sorted(dev_ids),
        }
        print(f"  track1/{dom:<10} docs={n_docs:>7}  q={len(by_qid):>4} "
              f"(tr {counts['train']['queries']}/dev {counts['dev']['queries']})  "
              f"steps={n_steps:>4} in {len(step_records):>4} records  "
              f"missing_gold={len(missing)}", flush=True)


# ------------------------------------------------------------- track 2 -----
def build_recor(raw, out, manifest, report):
    src = os.path.join(raw, "recor", "data")
    bench_dir = os.path.join(src, "benchmark")
    files = sorted(f for f in os.listdir(bench_dir) if f.endswith("_benchmark.jsonl"))
    for fn in files:
        upstream = fn[: -len("_benchmark.jsonl")]
        dom = upstream.lower()
        dst = os.path.join(out, "track2_recor", dom)
        os.makedirs(dst, exist_ok=True)

        # ---- corpus (never split) -----------------------------------------
        corpus_ids = set()
        n_docs = 0
        src_docs = os.path.join(src, "corpus", f"{upstream}_documents.jsonl")
        with open(src_docs, encoding="utf-8") as fin, \
             open(os.path.join(dst, "documents.jsonl"), "w", encoding="utf-8") as fout:
            for ln in fin:
                if not ln.strip():
                    continue
                d = json.loads(ln)
                fout.write(json.dumps({"doc_id": d["doc_id"], "content": d["content"]},
                                      ensure_ascii=False) + "\n")
                corpus_ids.add(d["doc_id"])
                n_docs += 1

        # ---- conversations (atomic split unit) -----------------------------
        convs = OrderedDict()
        with open(os.path.join(bench_dir, fn), encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    c = json.loads(ln)
                    convs[c["id"]] = c
        train_ids, dev_ids = split_ids(convs.keys(), f"recor:{dom}")

        counts = {}
        missing = set()
        for split, keep in (("train", train_ids), ("dev", dev_ids)):
            sel = [c for cid, c in convs.items() if cid in keep]
            with open(os.path.join(dst, f"benchmark_{split}.json"), "w",
                      encoding="utf-8") as f:
                json.dump(sel, f, ensure_ascii=False, indent=1)
            pairs, n_turns = [], 0
            for c in sel:
                for t in c["turns"]:
                    n_turns += 1
                    qid = f"{c['id']}_turn_{t['turn_id']}"  # official RECOR topic id
                    for d in t.get("gold_doc_ids") or []:
                        if d in corpus_ids:
                            pairs.append((qid, d))
                        else:
                            missing.add(d)  # upstream dangling id: not retrievable
            nq = write_qrels(os.path.join(dst, f"qrels_{split}.txt"), pairs)
            counts[split] = {"conversations": len(sel), "turns": n_turns, "qrels": nq}

        assert not (train_ids & dev_ids), f"{dom}: train/dev overlap"
        report["recor_missing_gold"][dom] = sorted(missing)

        manifest["track2_recor"][dom] = {
            "upstream_name": upstream,
            "dropped_gold_ids": sorted(missing),
            "documents": n_docs,
            "conversations_total": len(convs),
            "turns_total": counts["train"]["turns"] + counts["dev"]["turns"],
            "train": counts["train"], "dev": counts["dev"],
            "train_ids": sorted(train_ids), "dev_ids": sorted(dev_ids),
        }
        print(f"  track2/{dom:<18} docs={n_docs:>7}  conv={len(convs):>3} "
              f"(tr {counts['train']['conversations']}/dev {counts['dev']['conversations']})  "
              f"turns={manifest['track2_recor'][dom]['turns_total']:>4}  "
              f"missing_gold={len(missing)}", flush=True)


# ------------------------------------------------------------------ main ---
def main():
    ap = argparse.ArgumentParser()
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument("--raw", default=os.path.join(here, "..", "hf_raw"))
    ap.add_argument("--out", default=os.path.join(here, "..", "reteco_data"))
    args = ap.parse_args()
    raw, out = os.path.abspath(args.raw), os.path.abspath(args.out)
    os.makedirs(out, exist_ok=True)

    manifest = {
        "release": "RETECO SemEval-2027 train/dev",
        "split": {"scheme": "70/30 per domain", "seed": SEED,
                  "unit": {"track1_tempo": "query", "track2_recor": "conversation"},
                  "note": "Corpora are never split; retrieval uses the full domain corpus. "
                          "Track 1b steps and reformulation variants follow their parent query."},
        "upstream": {
            "tempo": {"dataset": TEMPO_PINS[0], "revision": TEMPO_PINS[1],
                      "url": f"https://huggingface.co/datasets/{TEMPO_PINS[0]}"},
            "recor": {"dataset": RECOR_PINS[0], "revision": RECOR_PINS[1],
                      "url": f"https://huggingface.co/datasets/{RECOR_PINS[0]}"},
        },
        "track1_tempo": {}, "track2_recor": {},
    }
    report = {"tempo_missing_gold": {}, "recor_missing_gold": {}}

    print("Track 1 (TEMPO):", flush=True)
    build_tempo(raw, out, manifest, report)
    print("Track 2 (RECOR):", flush=True)
    build_recor(raw, out, manifest, report)

    t1 = manifest["track1_tempo"].values()
    t2 = manifest["track2_recor"].values()
    totals = {
        "track1_documents": sum(d["documents"] for d in t1),
        "track1_queries": sum(d["queries_total"] for d in t1),
        "track1_steps": sum(d["steps_total"] for d in t1),
        "track2_documents": sum(d["documents"] for d in t2),
        "track2_conversations": sum(d["conversations_total"] for d in t2),
        "track2_turns": sum(d["turns_total"] for d in t2),
    }
    manifest["totals"] = totals
    with open(os.path.join(out, "split_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print("\nTOTALS", json.dumps(totals, indent=2))
    expected = {"track1_documents": 1654055, "track1_queries": 1730, "track1_steps": 3976,
                "track2_documents": 507141, "track2_conversations": 707, "track2_turns": 2971}
    for k, v in expected.items():
        flag = "OK " if totals[k] == v else "MISMATCH"
        print(f"  [{flag}] {k}: got {totals[k]}, published {v}")
    nmiss = sum(len(v) for v in report["tempo_missing_gold"].values()) + \
            sum(len(v) for v in report["recor_missing_gold"].values())
    manifest["dropped_gold_ids_total"] = nmiss
    with open(os.path.join(out, "split_manifest.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"  [OK ] upstream gold ids absent from any corpus, dropped from qrels: {nmiss}")


if __name__ == "__main__":
    main()
