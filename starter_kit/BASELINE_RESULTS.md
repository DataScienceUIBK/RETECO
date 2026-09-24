# RETECO official BM25 baseline — train and dev

Retrieval: verbatim `retrieval_bm25` from the upstream TEMPO and RECOR repos
(pyserini Lucene analyzer + gensim `LuceneBM25Model`, k1=0.9, b=0.4, top-1000).
Scoring: upstream `calculate_retrieval_metrics` — `pytrec_eval`, `ndcg_cut_10`.
Macro-averaged over domains, as both papers do.

Track 1 numbers are measured on **data v1.1** (Track 1 corpora deduplicated,
25 Sep 2026). On v1.0 the Track 1 macro averages were 1a 0.0879 / 0.0967 and
1b 0.0852 / 0.1063 (train / dev). Track 2 data did not change.

## Macro-average nDCG@10

| Sub-track | train | dev | published (full set) |
| --- | ---: | ---: | ---: |
| 1a · whole-query retrieval | 0.1075 | 0.1147 | 0.108 (TEMPO paper) |
| 1b · step-wise retrieval | 0.1024 | 0.1177 | not reported |
| 2a · Base (current turn only) | 0.1837 | 0.1827 | 0.185 (RECOR Table 3) |
| 2a · +History | 0.4539 | 0.4379 | 0.446 (RECOR Table 3) |

Our splits cover 70% / 30% of each domain, so exact equality with the
full-set published figures is not expected; Track 2 reproduces both published
BM25 configurations to within 0.003. The v1.1 Track 1 corpora are also
deduplicated, so they are smaller than the corpora used in the TEMPO paper.

## Per-domain nDCG@10

### Track 1 · TEMPO (data v1.1)

| Domain | 1a train | 1a dev | 1b train | 1b dev |
| --- | ---: | ---: | ---: | ---: |
| bitcoin | 0.0856 | 0.0370 | 0.0888 | 0.0299 |
| cardano | 0.1848 | 0.1027 | 0.1655 | 0.0627 |
| economics | 0.0382 | 0.0467 | 0.0300 | 0.0463 |
| genealogy | 0.1242 | 0.1949 | 0.1181 | 0.2183 |
| history | 0.0654 | 0.0873 | 0.0614 | 0.1015 |
| hsm | 0.1736 | 0.2489 | 0.1729 | 0.2140 |
| iota | 0.1563 | 0.3309 | 0.1403 | 0.4195 |
| law | 0.0946 | 0.0574 | 0.0854 | 0.0549 |
| monero | 0.0382 | 0.0320 | 0.0622 | 0.0113 |
| politics | 0.2810 | 0.2625 | 0.2403 | 0.2371 |
| quant | 0.0255 | 0.0237 | 0.0085 | 0.0403 |
| travel | 0.0506 | 0.0442 | 0.0423 | 0.0645 |
| workplace | 0.0798 | 0.0230 | 0.1162 | 0.0297 |

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
