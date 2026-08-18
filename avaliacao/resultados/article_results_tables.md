# Tabelas principais sugeridas

## Tabela 1 — Recuperação por pipeline

| Pipeline         | Section F1   | Section Recall   | All Required   |   Hit@10 |   MRR@10 |   nDCG@10 |   Retrieval Time (s) |
|:-----------------|:-------------|:-----------------|:---------------|---------:|---------:|----------:|---------------------:|
| Naive RAG        | N/A          | N/A              | N/A            |    0.157 |    0.103 |     0.108 |                 0.05 |
| Standard RAG     | 0.571        | 0.723            | 0.572          |    0.149 |    0.138 |     0.123 |                 8    |
| Agentic RAG      | 0.509        | 0.586            | 0.417          |    0.129 |    0.12  |     0.106 |                 8.83 |
| Hybrid Agent RAG | 0.490        | 0.547            | 0.394          |    0.122 |    0.105 |     0.094 |                 7.62 |
| Fusion RAG       | 0.395        | 0.463            | 0.328          |    0.101 |    0.132 |     0.099 |                10.02 |
| Graph RAG        | 0.378        | 0.457            | 0.317          |    0.096 |    0.086 |     0.072 |                 0.05 |
| Guarded RAG      | 0.475        | 0.858            | 0.744          |    0.201 |    0.212 |     0.178 |                38.97 |

Nota: métricas baseadas em seção não se aplicam ao Naive RAG porque esse pipeline não realiza roteamento por seção.

## Tabela 2 — Geração por pipeline

| Pipeline         |   BERTScore |   Faithfulness |   Answer Relevancy |   Response Completeness |   Clinical Safety |   Warning Preservation |   Inference Control |   Inference Time (s) |
|:-----------------|------------:|---------------:|-------------------:|------------------------:|------------------:|-----------------------:|--------------------:|---------------------:|
| Naive RAG        |       0.685 |          0.776 |              0.736 |                   0.564 |             0.753 |                  0.639 |               0.662 |                72.7  |
| Standard RAG     |       0.732 |          0.81  |              0.654 |                   0.447 |             0.706 |                  0.578 |               0.729 |                11.91 |
| Agentic RAG      |       0.726 |          0.772 |              0.634 |                   0.407 |             0.676 |                  0.515 |               0.701 |                14.52 |
| Hybrid Agent RAG |       0.719 |          0.717 |              0.546 |                   0.392 |             0.637 |                  0.49  |               0.681 |                24.76 |
| Fusion RAG       |       0.722 |          0.569 |              0.521 |                   0.379 |             0.533 |                  0.458 |               0.536 |                10.79 |
| Graph RAG        |       0.608 |          0.7   |              0.488 |                   0.333 |             0.6   |                  0.404 |               0.714 |                14.84 |
| Guarded RAG      |       0.749 |          0.854 |              0.809 |                   0.625 |             0.746 |                  0.7   |               0.732 |                51.51 |
