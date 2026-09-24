#!/usr/bin/env python3
"""Independent check of a dedup_track1.py output against the original release.

Reads both releases from disk and checks, per Track 1 domain:
  corpus   - new IDs unique; no two new docs share text; every old doc is either
             kept byte-for-byte or mapped to a kept doc with the same text
  qrels    - new qrels == old qrels with IDs mapped (duplicates collapsed);
             same topics; same number of distinct gold texts per topic
  gold     - every mapped gold ID points at a doc with the same text
  task     - examples/steps/guidance equal the old records with IDs mapped;
             every ID they name exists in the new corpus
  splits   - record IDs and order unchanged in every task file
Track 2 is checked to be byte-identical.

    python verify_dedup_track1.py --old reteco_data --new reteco_data_v1.1
"""
import argparse
import filecmp
import hashlib
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor

WS = re.compile(r"\s+")


def tkey(c):
    return hashlib.md5(WS.sub(" ", c or "").strip().encode("utf-8")).hexdigest()


def corpus(path):
    lines, keys = {}, {}
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                d = json.loads(ln)
                lines[d["id"]] = ln
                keys[d["id"]] = tkey(d["content"])
    return lines, keys


def qrels(path):
    q = defaultdict(set)
    with open(path, encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                t, _, d, r = ln.split()
                q[t].add(d)
    return q


def jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def apply_map(obj, m):
    if isinstance(obj, str):
        return m.get(obj, obj)
    if isinstance(obj, dict):
        return {k: apply_map(v, m) for k, v in obj.items()}
    if isinstance(obj, list):
        return [apply_map(x, m) for x in obj]
    return obj


def ids_in(obj, universe, out):
    if isinstance(obj, str):
        if obj in universe:
            out.add(obj)
    elif isinstance(obj, list):
        for x in obj:
            ids_in(x, universe, out)
    elif isinstance(obj, dict):
        for x in obj.values():
            ids_in(x, universe, out)


def same_modulo_collapse(old, new, universe):
    """new must equal old except that repeated doc IDs inside a plain ID list
    are collapsed to their first occurrence. Nothing else may be dropped."""
    if isinstance(old, dict) and isinstance(new, dict):
        return old.keys() == new.keys() and all(
            same_modulo_collapse(old[k], new[k], universe) for k in old)
    if isinstance(old, list) and isinstance(new, list):
        exp, seen = [], set()
        for x in old:
            if isinstance(x, str) and x in universe:
                if x in seen:
                    continue
                seen.add(x)
            exp.append(x)
        return len(exp) == len(new) and all(
            same_modulo_collapse(a, b, universe) for a, b in zip(exp, new))
    return old == new


def check_domain(args):
    old_root, new_root, dom = args
    o, n = os.path.join(old_root, dom), os.path.join(new_root, dom)
    errs = []
    old_lines, old_keys = corpus(os.path.join(o, "documents.jsonl"))
    new_lines, new_keys = corpus(os.path.join(n, "documents.jsonl"))
    m = json.load(open(os.path.join(n, "duplicate_map.json"), encoding="utf-8"))

    # corpus
    if len(set(new_keys.values())) != len(new_keys):
        errs.append("new corpus still contains duplicate texts")
    if len(new_keys) != len(set(old_keys.values())):
        errs.append("new corpus size != number of distinct old texts")
    if set(m) & set(new_lines):
        errs.append("a mapped-away ID is still in the new corpus")
    for i, ln in old_lines.items():
        if i in new_lines:
            if new_lines[i] != ln:
                errs.append(f"kept doc changed: {i}")
                break
        elif i not in m:
            errs.append(f"doc vanished without mapping: {i}")
            break
        elif m[i] not in new_lines or new_keys[m[i]] != old_keys[i]:
            errs.append(f"doc mapped to missing/different text: {i} -> {m[i]}")
            break

    # qrels + gold
    gold_pairs = 0
    for name in ("qrels", "qrels_steps"):
        for split in ("train", "dev"):
            oq = qrels(os.path.join(o, f"{name}_{split}.txt"))
            nq = qrels(os.path.join(n, f"{name}_{split}.txt"))
            if set(oq) != set(nq):
                errs.append(f"{name}_{split}: topic set changed")
            for t, docs in oq.items():
                gold_pairs += len(docs)
                if {m.get(d, d) for d in docs} != nq.get(t, set()):
                    errs.append(f"{name}_{split}/{t}: gold set not preserved")
                if any(d not in new_lines for d in nq.get(t, ())):
                    errs.append(f"{name}_{split}/{t}: gold ID missing from new corpus")
                elif len({old_keys[d] for d in docs}) != len({new_keys[d] for d in nq.get(t, ())}):
                    errs.append(f"{name}_{split}/{t}: distinct gold text count changed")

    # task files
    universe = set(old_lines)
    new_ids = set(new_lines)
    for name in ("examples", "steps", "guidance"):
        for split in ("train", "dev"):
            orecs = jsonl(os.path.join(o, f"{name}_{split}.jsonl"))
            nrecs = jsonl(os.path.join(n, f"{name}_{split}.jsonl"))
            if [r["id"] for r in orecs] != [r["id"] for r in nrecs]:
                errs.append(f"{name}_{split}: record IDs/order changed")
                continue
            for a, b in zip(orecs, nrecs):
                if not same_modulo_collapse(apply_map(a, m), b, new_ids):
                    errs.append(f"{name}_{split}/{a['id']}: content differs beyond ID mapping")
                    break
                if len(a.get("gold_passage_annotations", [])) != len(b.get("gold_passage_annotations", [])):
                    errs.append(f"{name}_{split}/{a['id']}: guidance annotations dropped")
                    break
            refs = set()
            ids_in(nrecs, universe, refs)
            if refs - set(new_lines):
                errs.append(f"{name}_{split}: names IDs absent from new corpus")

    # examples/steps gold_ids agree with qrels
    for split in ("train", "dev"):
        nq = qrels(os.path.join(n, f"qrels_{split}.txt"))
        for r in jsonl(os.path.join(n, f"examples_{split}.jsonl")):
            if set(r["gold_ids"]) != nq.get(r["id"], set()):
                errs.append(f"examples_{split}/{r['id']}: gold_ids != qrels")
        nq = qrels(os.path.join(n, f"qrels_steps_{split}.txt"))
        for r in jsonl(os.path.join(n, f"steps_{split}.jsonl")):
            for st in r["steps"]:
                if st["gold_ids"] and set(st["gold_ids"]) != nq.get(st["step_id"], set()):
                    errs.append(f"steps_{split}/{st['step_id']}: gold_ids != qrels")

    return dom, len(old_lines), len(new_lines), gold_pairs, errs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--old", required=True)
    ap.add_argument("--new", required=True)
    args = ap.parse_args()
    t_old = os.path.join(args.old, "track1_tempo")
    t_new = os.path.join(args.new, "track1_tempo")
    doms = sorted(os.listdir(t_old))
    ok = sorted(os.listdir(t_new)) == doms
    with ProcessPoolExecutor(13) as ex:
        for dom, a, b, g, errs in ex.map(check_domain, [(t_old, t_new, d) for d in doms]):
            status = "OK" if not errs else "FAIL"
            print(f"{status:4} {dom:10} docs {a:>7} -> {b:>7}  gold pairs checked {g:>5}")
            for e in errs[:10]:
                print("     ", e)
            ok &= not errs

    # Track 2 must be untouched
    o2, n2 = os.path.join(args.old, "track2_recor"), os.path.join(args.new, "track2_recor")
    for dom in sorted(os.listdir(o2)):
        files = sorted(os.listdir(os.path.join(o2, dom)))
        if files != sorted(os.listdir(os.path.join(n2, dom))):
            print(f"FAIL track2/{dom}: file list differs"); ok = False; continue
        _, mismatch, errors = filecmp.cmpfiles(os.path.join(o2, dom), os.path.join(n2, dom),
                                               files, shallow=False)
        if mismatch or errors:
            print(f"FAIL track2/{dom}: {mismatch + errors}"); ok = False
    print("track2 byte-identical" if ok else "")
    print("ALL CHECKS PASSED" if ok else "CHECKS FAILED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
