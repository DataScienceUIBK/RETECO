"""Pure-Python BM25 (Okapi) ranker -- no external dependencies.

Used as the RETECO starter baseline. Defaults (k1=0.9, b=0.4) follow common
BEIR practice for zero-shot retrieval; override on the CLI if desired.
"""
import re
from math import log

_TOKEN = re.compile(r"[A-Za-z0-9]+")


def tokenize(text):
    return _TOKEN.findall((text or "").lower())


class BM25:
    def __init__(self, doc_ids, doc_texts, k1=0.9, b=0.4):
        self.k1, self.b = k1, b
        self.doc_ids = list(doc_ids)
        self.docs = [tokenize(t) for t in doc_texts]
        self.N = len(self.docs)
        self.doc_len = [len(d) for d in self.docs]
        self.avgdl = (sum(self.doc_len) / self.N) if self.N else 0.0
        # document frequencies + per-doc term frequencies
        self.tf = []
        df = {}
        for d in self.docs:
            counts = {}
            for w in d:
                counts[w] = counts.get(w, 0) + 1
            self.tf.append(counts)
            for w in counts:
                df[w] = df.get(w, 0) + 1
        # BM25+ style idf (non-negative)
        self.idf = {w: log(1 + (self.N - n + 0.5) / (n + 0.5)) for w, n in df.items()}

    def _score(self, q_terms, i):
        score, dl, k1, b = 0.0, self.doc_len[i], self.k1, self.b
        tf_i = self.tf[i]
        for w in q_terms:
            if w not in tf_i:
                continue
            f = tf_i[w]
            denom = f + k1 * (1 - b + b * dl / (self.avgdl or 1))
            score += self.idf.get(w, 0.0) * (f * (k1 + 1)) / denom
        return score

    def search(self, query, top_k=100):
        """Return [(doc_id, score), ...] sorted by score desc (stable)."""
        q = tokenize(query)
        scored = [(self.doc_ids[i], self._score(q, i)) for i in range(self.N)]
        scored.sort(key=lambda x: (-x[1], x[0]))
        return scored[:top_k]
