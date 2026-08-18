# Tabelas principais sugeridas

## Tabela 1 — Desempenho médio de recuperação por pipeline

| Pipeline | Section Precision | Section Recall | F1-Score | All Required | Hit@10 | MRR@10 | nDCG@10 | Retrieval Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Naive RAG | N/A | N/A | N/A | N/A | 0.157 | 0.103 | 0.108 | 0.053 |
| Standard RAG | 0.531 | 0.723 | 0.571 | 0.572 | 0.149 | 0.138 | 0.123 | 7.997 |
| Agentic RAG | 0.497 | 0.586 | 0.509 | 0.417 | 0.129 | 0.12 | 0.106 | 8.834 |
| Hybrid Agentic RAG | 0.483 | 0.547 | 0.49 | 0.394 | 0.122 | 0.105 | 0.094 | 7.618 |
| Fusion RAG | 0.377 | 0.463 | 0.395 | 0.328 | 0.101 | 0.132 | 0.099 | 10.024 |
| Graph RAG | 0.358 | 0.457 | 0.378 | 0.317 | 0.096 | 0.086 | 0.072 | 0.048 |
| Guarded Hybrid Agentic Fusion RAG | 0.354 | 0.858 | 0.475 | 0.744 | 0.201 | 0.212 | 0.178 | 38.972 |

Nota: métricas de seção não se aplicam ao Naive RAG, pois este pipeline não realiza roteamento em nível de seção.

## Tabela 2 — Desempenho médio de geração por pipeline

| Pipeline | BERTScore | Faithfulness | Answer Relevancy | Response Completeness | Clinical Safety | Warning Preservation | Inference Control | Inference Time (s) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Naive RAG | 0.685 | 0.776 | 0.736 | 0.564 | 0.753 | 0.639 | 0.662 | 72.705 |
| Standard RAG | 0.732 | 0.81 | 0.654 | 0.447 | 0.706 | 0.578 | 0.729 | 11.906 |
| Agentic RAG | 0.726 | 0.772 | 0.634 | 0.407 | 0.676 | 0.515 | 0.701 | 14.519 |
| Hybrid Agentic RAG | 0.719 | 0.717 | 0.546 | 0.392 | 0.638 | 0.49 | 0.681 | 24.756 |
| Fusion RAG | 0.722 | 0.569 | 0.521 | 0.379 | 0.533 | 0.458 | 0.536 | 10.787 |
| Graph RAG | 0.608 | 0.7 | 0.488 | 0.333 | 0.6 | 0.404 | 0.714 | 14.842 |
| Guarded Hybrid Agentic Fusion RAG | 0.749 | 0.854 | 0.809 | 0.625 | 0.746 | 0.7 | 0.732 | 51.514 |

## Tabela 3 — Trade-off médio entre qualidade e tempo

| Pipeline | Total Time (s) | Retrieval Time (s) | Inference Time (s) | Key Judge Score |
| --- | ---: | ---: | ---: | ---: |
| Naive RAG | 72.75758333333334 | 0.05276666666666668 | 72.70481666666667 | 0.7074305555555555 |
| Standard RAG | 19.903166666666664 | 7.996794444444443 | 11.906372222222222 | 0.705625 |
| Agentic RAG | 23.352905555555555 | 8.83373888888889 | 14.519166666666665 | 0.6663194444444445 |
| Hybrid Agentic RAG | 32.37446111111112 | 7.618133333333334 | 24.75632777777778 | 0.63125 |
| Fusion RAG | 20.810605555555554 | 10.023888888888889 | 10.786716666666665 | 0.5241666666666667 |
| Graph RAG | 14.88931111111111 | 0.04774444444444445 | 14.841566666666667 | 0.6045138888888889 |
| Guarded Hybrid Agentic Fusion RAG | 90.48618888888889 | 38.97238333333333 | 51.51380555555556 | 0.7580555555555556 |