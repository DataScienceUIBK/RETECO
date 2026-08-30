# RETECO official BM25 baseline — train and dev

Retrieval: verbatim `retrieval_bm25` from the upstream TEMPO and RECOR repos
(pyserini Lucene analyzer + gensim `LuceneBM25Model`, k1=0.9, b=0.4, top-1000).
Scoring: upstream `calculate_retrieval_metrics` — `pytrec_eval`, `ndcg_cut_10`.
Macro-averaged over domains, as both papers do.

## Macro-average nDCG@10

| Sub-track | train | dev | published (full set) |
| --- | ---: | ---: | ---: |
| 1a · whole-query retrieval | 0.0879 | 0.0967 | 0.108 (TEMPO paper) |
| 1b · step-wise retrieval | 0.0852 | 0.1063 | not reported |
| 2a · Base (current turn only) | 0.1837 | 0.1827 | 0.185 (RECOR Table 3) |
| 2a · +History | 0.4539 | 0.4379 | 0.446 (RECOR Table 3) |

Our splits cover 70% / 30% of each domain, so exact equality with the
full-set published figures is not expected; Track 2 reproduces both published
BM25 configurations to within 0.003.

## Per-domain nDCG@10

### Track 1 · TEMPO

| Domain | 1a train | 1a dev | 1b train | 1b dev |
| --- | ---: | ---: | ---: | ---: |
| bitcoin | 0.0695 | 0.0263 | 0.0774 | 0.0205 |
| cardano | 0.1349 | 0.0851 | 0.1174 | 0.0554 |
| economics | 0.0382 | 0.0480 | 0.0278 | 0.0517 |
| genealogy | 0.1003 | 0.1677 | 0.0982 | 0.2060 |
| history | 0.0691 | 0.0877 | 0.0651 | 0.0989 |
| hsm | 0.1627 | 0.2239 | 0.1591 | 0.2084 |
| iota | 0.0199 | 0.2083 | 0.0000 | 0.3289 |
| law | 0.0943 | 0.0574 | 0.0846 | 0.0549 |
| monero | 0.0278 | 0.0252 | 0.0517 | 0.0103 |
| politics | 0.2792 | 0.2550 | 0.2425 | 0.2306 |
| quant | 0.0255 | 0.0218 | 0.0085 | 0.0374 |
| travel | 0.0429 | 0.0275 | 0.0378 | 0.0492 |
| workplace | 0.0777 | 0.0230 | 0.1369 | 0.0302 |

### Track 2 · RECOR

| Domain | 2a train | 2a dev | 2a_hist train | 2a_hist dev |
| --- | ---: | ---: | ---: | ---: |
| biology | 0.2250 | 0.2034 | 0.6369 | 0.6065 |
| drones | 0.1400 | 0.1695 | 0.3162 | 0.2954 |
| earth_science | 0.2757 | 0.2195 | 0.6324 | 0.6264 |
| economics | 0.1573 | 0.1629 | 0.4593 | 0.4739 |
| hardware | 0.1472 | 0.1605 | 0.2935 | 0.3378 |
| law | 0.1047 | 0.1147 | 0.2721 | 0.3437 |
| medicalsciences | 0.1188 | 0.1168 | 0.2267 | 0.1730 |
| politics | 0.1609 | 0.1514 | 0.4423 | 0.3219 |
| psychology | 0.2208 | 0.2596 | 0.5558 | 0.5726 |
| robotics | 0.1847 | 0.1574 | 0.5773 | 0.5123 |
| sustainable_living | 0.2851 | 0.2938 | 0.5801 | 0.5531 |
