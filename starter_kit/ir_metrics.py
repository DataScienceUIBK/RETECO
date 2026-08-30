"""RETECO official evaluation metrics (pure Python, no dependencies).

Implements the metrics used by both RETECO tracks:

  * nDCG@k          -- official leaderboard metric (both tracks)
  * Temporal Precision@k (TP)   -- position-weighted precision of temporally relevant docs
  * Temporal Relevance@k (TR)   -- fraction of top-k judged temporally relevant
  * Temporal Coverage@k  (TC)   -- fraction of the query's required time periods covered
  * NDCG|FC@k       -- nDCG@k over queries that achieve full temporal coverage (TC==1)

On the HIDDEN test, temporal relevance and period coverage are assigned by the
LLM-as-judge (documented prompts + golden-case calibration + human spot-check).
For the OFFLINE pilot scorer here, the gold relevance labels in `qrels` are used
as the temporal-relevance oracle, and the per-query step files supply the set of
required time periods (one step == one required period). This mirrors how the
hidden-test scorer will consume judge labels, so the same code path is reused.
"""
from math import log2


# ---------------------------------------------------------------- core DCG ----
def _dcg(rels):
    """Discounted cumulative gain of an ordered list of relevance grades."""
    return sum(r / log2(i + 2) for i, r in enumerate(rels))  # i=0 -> 1/log2(2)=1


def ndcg_at_k(ranked_docids, gold, k=10):
    """Binary nDCG@k. `gold` is a set/dict of relevant doc ids (grade 1)."""
    grades = [1.0 if d in gold else 0.0 for d in ranked_docids[:k]]
    ideal = sorted([1.0] * min(len(gold), k), reverse=True)
    idcg = _dcg(ideal)
    return (_dcg(grades) / idcg) if idcg > 0 else 0.0


# ------------------------------------------------------ temporal metrics -------
def temporal_relevance_at_k(ranked_docids, temporally_relevant, k=10):
    """TR@k: fraction of the top-k that is temporally relevant."""
    top = ranked_docids[:k]
    if not top:
        return 0.0
    return sum(1 for d in top if d in temporally_relevant) / len(top)


def temporal_precision_at_k(ranked_docids, temporally_relevant, k=10):
    """TP@k: position-weighted precision (rewards ranking relevant docs earlier).

    TP@k = sum_i w_i * rel_i / sum_i w_i ,  w_i = 1/log2(i+1), i=1..k
    """
    top = ranked_docids[:k]
    num = den = 0.0
    for i, d in enumerate(top):
        w = 1.0 / log2(i + 2)
        den += w
        if d in temporally_relevant:
            num += w
    return (num / den) if den > 0 else 0.0


def temporal_coverage_at_k(ranked_docids, period_gold, k=10):
    """TC@k: fraction of required time periods covered by >=1 doc in the top-k.

    `period_gold` is a list of gold-id sets, one per required period (step).
    """
    if not period_gold:
        return None  # query has no defined periods -> excluded from TC
    top = set(ranked_docids[:k])
    covered = sum(1 for gs in period_gold if top & set(gs))
    return covered / len(period_gold)


# ------------------------------------------------------------- aggregation -----
def mean(xs):
    xs = [x for x in xs if x is not None]
    return (sum(xs) / len(xs)) if xs else 0.0
