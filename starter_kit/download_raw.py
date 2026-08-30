#!/usr/bin/env python3
"""Download full TEMPO and RECOR releases at the revisions pinned in the RETECO manifest."""
import os
from huggingface_hub import snapshot_download

BASE = "/data/fs201213/aa17626/semeval/hf_raw"
PINS = {
    "tempo": ("tempo26/Tempo", "f9df06c05688225e37701974d23c8e3c5d4efaf6"),
    "recor": ("RECOR-Benchmark/RECOR", "d9faa639019dcfa1a1fea2aece55ebcba3083c00"),
}

for name, (repo, rev) in PINS.items():
    dest = os.path.join(BASE, name)
    print(f"[{name}] {repo}@{rev[:8]} -> {dest}", flush=True)
    p = snapshot_download(repo_id=repo, repo_type="dataset", revision=rev,
                          local_dir=dest, max_workers=8)
    print(f"[{name}] done: {p}", flush=True)
print("ALL DONE", flush=True)
