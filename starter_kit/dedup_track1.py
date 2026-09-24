#!/usr/bin/env python3
"""Remove duplicate documents from the Track 1 (TEMPO) corpora without losing gold.

Two documents are duplicates when their text is identical after collapsing
whitespace. Near-duplicates are deliberately kept: in a temporal task, pages
that differ only in a date or version number are different evidence.

For each group of duplicates one ID is kept:
  1. an ID referenced by any task file (qrels, gold_ids, guidance) if the
     group has one -- the smallest such ID when several are referenced;
  2. otherwise the smallest ID in the group.
Every other ID is removed from documents.jsonl and renamed to the kept ID
wherever it appears in the task files. ID lists (gold_ids, qrels) that end up
naming the same document twice are collapsed, keeping the first occurrence;
guidance annotations are never dropped, so a record may then carry two
annotations with the same doc_id. The removed ->
kept mapping is written to <domain>/duplicate_map.json.

Track 2 is copied unchanged.

    python dedup_track1.py --src reteco_data --dst reteco_data_v1.1
"""
import argparse
import hashlib
import json
import os
import re
import shutil
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

WS = re.compile(r"\s+")
SPLITS = ("train", "dev")
JSONL_FILES = ("examples", "steps", "guidance")
QRELS_FILES = ("qrels", "qrels_steps")


def text_key(content):
    return hashlib.md5(WS.sub(" ", content or "").strip().encode("utf-8")).hexdigest()


def read_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")


def collect_ids(obj, corpus_ids, out):
    if isinstance(obj, str):
        if obj in corpus_ids:
            out.add(obj)
    elif isinstance(obj, list):
        for x in obj:
            collect_ids(x, corpus_ids, out)
    elif isinstance(obj, dict):
        for x in obj.values():
            collect_ids(x, corpus_ids, out)


def remap(obj, id_map, stats):
    """Rename removed IDs; collapse lists that now name a document twice."""
    if isinstance(obj, str):
        if obj in id_map:
            stats["id_refs_renamed"] += 1
            return id_map[obj]
        return obj
    if isinstance(obj, dict):
        return {k: remap(v, id_map, stats) for k, v in obj.items()}
    if isinstance(obj, list):
        items = [remap(x, id_map, stats) for x in obj]
        out, seen = [], set()
        for x in items:
            # only plain ID lists (gold_ids) are collapsed; annotation records
            # are all kept even when two now name the same document
            if isinstance(x, str) and x in id_map.values_set:
                if x in seen:
                    stats["list_items_collapsed"] += 1
                    continue
                seen.add(x)
            out.append(x)
        return out
    return obj


class IdMap(dict):
    """removed_id -> kept_id, plus the set of all corpus IDs (for list collapsing)."""
    values_set = frozenset()


def dedup_domain(args):
    src, dst, dom = args
    sdir, ddir = os.path.join(src, dom), os.path.join(dst, dom)
    os.makedirs(ddir, exist_ok=True)

    # pass 1: corpus IDs and text keys, in file order
    ids, keys = [], []
    with open(os.path.join(sdir, "documents.jsonl"), encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                d = json.loads(ln)
                ids.append(d["id"])
                keys.append(text_key(d["content"]))
    corpus_ids = set(ids)
    assert len(corpus_ids) == len(ids), f"{dom}: duplicate IDs in corpus"

    # every ID referenced by any task file is protected
    task = {}
    referenced = set()
    for name in JSONL_FILES:
        for split in SPLITS:
            recs = read_jsonl(os.path.join(sdir, f"{name}_{split}.jsonl"))
            task[(name, split)] = recs
            collect_ids(recs, corpus_ids, referenced)
    qrels = {}
    for name in QRELS_FILES:
        for split in SPLITS:
            rows = []
            with open(os.path.join(sdir, f"{name}_{split}.txt"), encoding="utf-8") as f:
                for ln in f:
                    if ln.strip():
                        rows.append(ln.rstrip("\n").split("\t"))
            qrels[(name, split)] = rows
            referenced.update(r[2] for r in rows)
    missing = referenced - corpus_ids
    assert not missing, f"{dom}: referenced IDs absent from corpus: {sorted(missing)[:5]}"

    # choose one ID per group
    groups = defaultdict(list)
    for i, k in zip(ids, keys):
        groups[k].append(i)
    id_map = IdMap()
    for members in groups.values():
        if len(members) < 2:
            continue
        refs = [m for m in members if m in referenced]
        keep = min(refs) if refs else min(members)
        for m in members:
            if m != keep:
                id_map[m] = keep
    id_map.values_set = frozenset(corpus_ids)

    # pass 2: write kept documents, original lines byte-for-byte
    kept = 0
    with open(os.path.join(sdir, "documents.jsonl"), encoding="utf-8") as fin, \
         open(os.path.join(ddir, "documents.jsonl"), "w", encoding="utf-8") as fout:
        idx = 0
        for ln in fin:
            if not ln.strip():
                continue
            if ids[idx] not in id_map:
                fout.write(ln if ln.endswith("\n") else ln + "\n")
                kept += 1
            idx += 1

    stats = defaultdict(int)
    for (name, split), recs in task.items():
        write_jsonl(os.path.join(ddir, f"{name}_{split}.jsonl"),
                    [remap(r, id_map, stats) for r in recs])

    qrels_counts = {}
    for (name, split), rows in qrels.items():
        out, seen = [], set()
        for qid, it, doc, rel in rows:
            doc = id_map.get(doc, doc)
            if (qid, doc) in seen:
                stats["qrels_lines_collapsed"] += 1
                continue
            seen.add((qid, doc))
            out.append((qid, it, doc, rel))
        with open(os.path.join(ddir, f"{name}_{split}.txt"), "w", encoding="utf-8") as f:
            for row in out:
                f.write("\t".join(row) + "\n")
        qrels_counts[(name, split)] = len(out)

    with open(os.path.join(ddir, "duplicate_map.json"), "w", encoding="utf-8") as f:
        json.dump(dict(sorted(id_map.items())), f, indent=0, ensure_ascii=False)

    gold_renamed = sorted(i for i in referenced if i in id_map)
    return dict(domain=dom, documents_before=len(ids), documents_after=kept,
                documents_removed=len(id_map), duplicate_groups=sum(
                    1 for g in groups.values() if len(g) > 1),
                gold_ids_renamed=len(gold_renamed),
                id_refs_renamed=stats["id_refs_renamed"],
                list_items_collapsed=stats["list_items_collapsed"],
                qrels_lines_collapsed=stats["qrels_lines_collapsed"],
                qrels_counts={f"{n}_{s}": c for (n, s), c in qrels_counts.items()})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    ap.add_argument("--workers", type=int, default=13)
    args = ap.parse_args()
    src1 = os.path.join(args.src, "track1_tempo")
    dst1 = os.path.join(args.dst, "track1_tempo")
    assert not os.path.exists(args.dst), f"{args.dst} exists; refusing to overwrite"
    os.makedirs(dst1)

    doms = sorted(os.listdir(src1))
    with ProcessPoolExecutor(args.workers) as ex:
        report = list(ex.map(dedup_domain, [(src1, dst1, d) for d in doms]))

    shutil.copytree(os.path.join(args.src, "track2_recor"),
                    os.path.join(args.dst, "track2_recor"))
    with open(os.path.join(args.dst, "dedup_report.json"), "w") as f:
        json.dump(report, f, indent=1)
    for r in report:
        print(f"{r['domain']:10} {r['documents_before']:>8} -> {r['documents_after']:>8}"
              f"  removed {r['documents_removed']:>7}  gold renamed {r['gold_ids_renamed']:>3}"
              f"  qrels collapsed {r['qrels_lines_collapsed']:>3}"
              f"  list items collapsed {r['list_items_collapsed']:>3}")
    b = sum(r["documents_before"] for r in report)
    a = sum(r["documents_after"] for r in report)
    print(f"TOTAL {b} -> {a}  removed {b - a} ({100 * (b - a) / b:.1f}%)")


if __name__ == "__main__":
    main()
