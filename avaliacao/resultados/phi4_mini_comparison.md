# Comparação Intramodelo - Phi4 Mini (ollama:phi4-mini)

Este relatório compara de forma objetiva o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG** na recuperação e na geração de respostas, além de reportar os tempos médios de execução obtidos com o modelo **Phi4 Mini**.

> [!NOTE]
> **Destaque Visual:** Os melhores resultados em cada coluna estão destacados em **negrito** (maiores valores para pontuações de acurácia/recuperação e menores valores para taxas de falhas e tempos de latência).

## Glossário de Métricas
*   **Final Score (Judge):** Média aritmética (de 0.0 a 1.0) das avaliações do LLM-as-a-judge (ChatGPT / Gemini) nos 11 critérios individuais listados na seção 3.
*   **Falhas Críticas (%):** Proporção de respostas que continham erros severos sob a ótica de segurança ou alucinação.
*   **Context Recall / Precision:** Revocação e precisão do contexto selecionado pelo RAG em relação às informações necessárias para a resposta.
*   **Chunk Recall@K / MRR@K:** Métricas de recuperação no nível de chunk. Medem a proporção de trechos do gabarito recuperados e a posição (ranking) em que aparecem.
*   **Section Recall / Precision:** Grau de correspondência entre as seções formais da bula recuperadas pelo pipeline (ex: Posologia, Contraindicação) e aquelas esperadas no gabarito.
*   **ROUGE-L / BLEU:** Métricas léxicas automáticas comparando o texto da resposta gerada com a resposta de referência.
*   **Tempo Rec. (s):** Tempo médio gasto no processo de busca e recuperação de contexto (vetorial, agente ou grafo).
*   **Tempo Inf. (s):** Tempo médio gasto pelo LLM local para inferência/geração da resposta final.

---

## 1. Resultados Detalhados por Dificuldade

### Perguntas Fáceis (Easy)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7706 | 40.0% | 0.8133 | 0.6400 | 0.1222 | 0.1963 | 0.1548 | 0.0000 | 0.0000 | **0.3597** | **0.1565** | 0.05s | 161.14s |
| Standard RAG | 0.6797 | 53.3% | 0.6267 | 0.6267 | 0.1222 | 0.1444 | 0.1259 | 0.5333 | 0.2667 | 0.2708 | 0.0763 | 2.53s | 4.16s |
| Agentic RAG | 0.6267 | 80.0% | 0.4667 | 0.4400 | 0.0667 | 0.0667 | 0.0667 | 0.2667 | 0.2000 | 0.1658 | 0.0327 | 4.23s | 39.21s |
| Hybrid Agent RAG | 0.5509 | 86.7% | 0.3600 | 0.3467 | 0.0556 | 0.0556 | 0.0519 | 0.2000 | 0.2000 | 0.1884 | 0.0417 | 2.28s | 2.53s |
| Fusion RAG | 0.6564 | 40.0% | 0.6933 | 0.7200 | 0.1667 | 0.1667 | 0.1667 | 0.5333 | 0.4000 | 0.2644 | 0.1088 | 2.50s | 3.49s |
| Graph RAG | 0.5624 | 100.0% | 0.7733 | 0.6800 | 0.0000 | 0.0000 | 0.0000 | 0.6000 | **0.4522** | 0.0363 | 0.0000 | **0.04s** | **0.00s** |
| Guarded RAG | **0.7755** | **26.7%** | **0.8800** | **0.7600** | **0.1741** | **0.2074** | **0.2476** | **0.8667** | 0.2384 | 0.3536 | 0.1288 | 34.58s | 17.83s |

### Perguntas Médias (Medium)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **0.7709** | **33.3%** | **0.9467** | 0.6800 | 0.1259 | 0.2296 | 0.1319 | 0.0000 | 0.0000 | **0.3422** | **0.1274** | 0.04s | 6.40s |
| Standard RAG | 0.5318 | 80.0% | 0.4800 | 0.4667 | 0.0815 | 0.1074 | 0.1148 | 0.4889 | **0.5556** | 0.2458 | 0.0582 | 2.70s | 4.08s |
| Agentic RAG | 0.6261 | 60.0% | 0.6267 | 0.5333 | 0.0556 | 0.0852 | 0.1000 | 0.4222 | 0.3000 | 0.2734 | 0.0864 | 3.18s | 4.57s |
| Hybrid Agent RAG | 0.6054 | 66.7% | 0.5333 | 0.5333 | 0.0852 | 0.1074 | 0.1037 | 0.4111 | 0.4222 | 0.2277 | 0.0449 | 3.02s | 4.57s |
| Fusion RAG | 0.6339 | 53.3% | 0.7467 | 0.7600 | 0.1778 | 0.1778 | 0.1963 | 0.4111 | 0.4333 | 0.2895 | 0.0888 | 5.45s | 4.35s |
| Graph RAG | 0.5136 | 100.0% | 0.7600 | 0.6400 | 0.0000 | 0.0000 | 0.0000 | 0.3222 | 0.3000 | 0.0279 | 0.0000 | **0.04s** | **0.00s** |
| Guarded RAG | 0.7576 | 46.7% | **0.9467** | **0.8533** | **0.2370** | **0.2481** | **0.2296** | **0.7778** | 0.4016 | 0.3323 | 0.1164 | 41.94s | 24.31s |

### Perguntas Difáceis (Hard)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.6588 | **46.7%** | 0.9333 | 0.7467 | 0.0778 | 0.1722 | 0.1211 | 0.0000 | 0.0000 | 0.2815 | 0.0979 | 0.09s | 10.40s |
| Standard RAG | 0.5021 | 80.0% | 0.4267 | 0.4400 | 0.0704 | 0.0778 | 0.1389 | 0.4333 | **0.7500** | 0.2070 | 0.0376 | 3.27s | 5.14s |
| Agentic RAG | 0.5900 | 80.0% | 0.6800 | 0.6667 | 0.0704 | 0.0889 | 0.1247 | 0.4389 | 0.4411 | 0.2406 | 0.0672 | 3.63s | 6.52s |
| Hybrid Agent RAG | 0.5621 | 73.3% | 0.6933 | 0.5867 | 0.0870 | 0.1259 | 0.1213 | 0.4833 | 0.3889 | 0.2440 | 0.0692 | 3.40s | 9.92s |
| Fusion RAG | 0.4779 | 73.3% | 0.5733 | 0.5867 | 0.0833 | 0.0907 | 0.1267 | 0.2278 | 0.3556 | 0.2400 | 0.0626 | 5.58s | 8.23s |
| Graph RAG | 0.5003 | 100.0% | 0.6400 | 0.4800 | 0.0000 | 0.0000 | 0.0000 | 0.3500 | 0.2833 | 0.0178 | 0.0000 | **0.04s** | **0.00s** |
| Guarded RAG | **0.6794** | 53.3% | **0.9867** | **0.8267** | **0.1685** | **0.2167** | **0.2452** | **0.7000** | 0.3556 | **0.3277** | **0.1252** | 45.10s | 40.34s |

---

## 2. Comparativo Consolidado por Pipeline (Média Geral)

A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline, unindo todas as dificuldades de perguntas:

| Pipeline | Média Final Score | Média Falhas Críticas | Média Chunk Recall@3 | Média Chunk Recall@10 | Média Chunk MRR@10 | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7334 | **40.0%** | 0.1086 | 0.1994 | 0.1359 | 0.8978 | 0.6889 | 0.3278 | **0.1273** | 0.06s | 59.31s |
| Standard RAG | 0.5712 | 71.1% | 0.0914 | 0.1099 | 0.1265 | 0.5111 | 0.5111 | 0.2412 | 0.0574 | 2.83s | 4.46s |
| Agentic RAG | 0.6142 | 73.3% | 0.0642 | 0.0802 | 0.0971 | 0.5911 | 0.5467 | 0.2266 | 0.0621 | 3.68s | 16.77s |
| Hybrid Agent RAG | 0.5728 | 75.6% | 0.0759 | 0.0963 | 0.0923 | 0.5289 | 0.4889 | 0.2200 | 0.0519 | 2.90s | 5.67s |
| Fusion RAG | 0.5894 | 55.6% | 0.1426 | 0.1451 | 0.1632 | 0.6711 | 0.6889 | 0.2646 | 0.0867 | 4.51s | 5.36s |
| Graph RAG | 0.5255 | 100.0% | 0.0000 | 0.0000 | 0.0000 | 0.7244 | 0.6000 | 0.0273 | 0.0000 | **0.04s** | **0.00s** |
| Guarded RAG | **0.7375** | 42.2% | **0.1932** | **0.2241** | **0.2408** | **0.9378** | **0.8133** | **0.3378** | 0.1235 | 40.54s | 27.50s |

---

## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge

Detalhamento das médias obtidas em cada um dos **11 critérios individuais** avaliados pelo juiz (escala de 0.0 a 1.0):

### Critérios - Perguntas Fáceis (Easy)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8133 | 0.6400 | 0.7833 | 0.9067 | 0.8000 | **0.6500** | 0.8333 | 0.7333 | **0.7500** | 0.7667 | 0.8000 |
| Standard RAG | 0.6267 | 0.6267 | 0.5333 | 0.8533 | 0.7200 | 0.4500 | 0.7833 | 0.6333 | 0.6500 | 0.7833 | 0.8167 |
| Agentic RAG | 0.4667 | 0.4400 | 0.3167 | 0.9200 | 0.5333 | 0.2500 | 0.8833 | 0.7167 | 0.5833 | **0.9000** | 0.8833 |
| Hybrid Agent RAG | 0.3600 | 0.3467 | 0.1833 | **0.9333** | 0.5200 | 0.1333 | 0.9000 | 0.6167 | 0.3833 | 0.7833 | 0.9000 |
| Fusion RAG | 0.6933 | 0.7200 | 0.5833 | 0.6267 | **0.8133** | 0.5000 | 0.5833 | 0.5833 | 0.6500 | **0.9000** | 0.5667 |
| Graph RAG | 0.7733 | 0.6800 | 0.6833 | 0.6000 | 0.2000 | 0.0000 | **1.0000** | **0.7500** | 0.0000 | 0.5000 | **1.0000** |
| Guarded RAG | **0.8800** | **0.7600** | **0.8333** | 0.8533 | 0.7867 | 0.6167 | 0.8000 | 0.7167 | 0.6833 | 0.8167 | 0.7833 |

### Critérios - Perguntas Médias (Medium)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **0.9467** | 0.6800 | **0.9333** | 0.7467 | **0.8400** | **0.6500** | 0.6833 | **0.8167** | **0.7167** | 0.8167 | 0.6500 |
| Standard RAG | 0.4800 | 0.4667 | 0.3167 | 0.7733 | 0.5467 | 0.2333 | 0.7000 | 0.5667 | 0.4167 | 0.6833 | 0.6667 |
| Agentic RAG | 0.6267 | 0.5333 | 0.5333 | 0.8267 | 0.6667 | 0.3833 | 0.7833 | 0.6167 | 0.4000 | 0.7667 | 0.7500 |
| Hybrid Agent RAG | 0.5333 | 0.5333 | 0.4167 | **0.8400** | 0.5200 | 0.2667 | 0.7833 | 0.6833 | 0.4500 | 0.8667 | 0.7667 |
| Fusion RAG | 0.7467 | 0.7600 | 0.6333 | 0.6133 | 0.7200 | 0.4500 | 0.5833 | 0.4667 | 0.5667 | **0.9000** | 0.5333 |
| Graph RAG | 0.7600 | 0.6400 | 0.7000 | 0.6000 | 0.2000 | 0.0000 | **1.0000** | 0.5000 | 0.0000 | 0.2500 | **1.0000** |
| Guarded RAG | **0.9467** | **0.8533** | **0.9333** | 0.7467 | 0.7867 | 0.6000 | 0.6667 | 0.7167 | **0.7167** | 0.7500 | 0.6167 |

### Critérios - Perguntas Difáceis (Hard)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.9333 | 0.7467 | 0.8833 | 0.6400 | 0.6933 | 0.4833 | 0.4667 | 0.6833 | **0.5000** | 0.7667 | 0.4500 |
| Standard RAG | 0.4267 | 0.4400 | 0.2833 | **0.7867** | 0.5200 | 0.1833 | 0.7333 | 0.5000 | 0.2500 | 0.6833 | 0.7167 |
| Agentic RAG | 0.6800 | 0.6667 | 0.6000 | 0.7067 | 0.5867 | 0.3000 | 0.6667 | 0.5333 | 0.4000 | 0.7500 | 0.6000 |
| Hybrid Agent RAG | 0.6933 | 0.5867 | 0.6000 | 0.7200 | 0.6000 | 0.3333 | 0.6000 | 0.5000 | 0.3000 | 0.7000 | 0.5500 |
| Fusion RAG | 0.5733 | 0.5867 | 0.4500 | 0.5200 | 0.5600 | 0.2667 | 0.4167 | 0.2833 | 0.3833 | **0.8333** | 0.3833 |
| Graph RAG | 0.6400 | 0.4800 | 0.5333 | 0.4000 | 0.2000 | 0.0000 | **1.0000** | **0.7500** | 0.0000 | 0.5000 | **1.0000** |
| Guarded RAG | **0.9867** | **0.8267** | **0.9833** | 0.6533 | **0.7733** | **0.5333** | 0.5000 | 0.5500 | 0.4833 | 0.7000 | 0.4833 |

### Critérios - Média Geral (Consolidado de Todas as Dificuldades)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8978 | 0.6889 | 0.8667 | 0.7644 | 0.7778 | **0.5944** | 0.6611 | **0.7444** | **0.6556** | 0.7833 | 0.6333 |
| Standard RAG | 0.5111 | 0.5111 | 0.3778 | 0.8044 | 0.5956 | 0.2889 | 0.7389 | 0.5667 | 0.4389 | 0.7167 | 0.7333 |
| Agentic RAG | 0.5911 | 0.5467 | 0.4833 | 0.8178 | 0.5956 | 0.3111 | 0.7778 | 0.6222 | 0.4611 | 0.8056 | 0.7444 |
| Hybrid Agent RAG | 0.5289 | 0.4889 | 0.4000 | **0.8311** | 0.5467 | 0.2444 | 0.7611 | 0.6000 | 0.3778 | 0.7833 | 0.7389 |
| Fusion RAG | 0.6711 | 0.6889 | 0.5556 | 0.5867 | 0.6978 | 0.4056 | 0.5278 | 0.4444 | 0.5333 | **0.8778** | 0.4944 |
| Graph RAG | 0.7244 | 0.6000 | 0.6389 | 0.5333 | 0.2000 | 0.0000 | **1.0000** | 0.6667 | 0.0000 | 0.4167 | **1.0000** |
| Guarded RAG | **0.9378** | **0.8133** | **0.9167** | 0.7511 | **0.7822** | 0.5833 | 0.6556 | 0.6611 | 0.6278 | 0.7556 | 0.6278 |

---

## 4. Notas Técnicas sobre o Pipeline "Naive RAG"

O **Naive RAG** apresenta valor `0.0000` em **Section Recall** e **Section Precision**.

### Explicação Técnica:
1. **Indexação Direta:** O Naive RAG fatia e indexa os textos de forma sequencial pura, sem estruturar o banco de dados vetorial por seções lógicas da bula (como fazem os outros pipelines). Por isso, ele não preenche a coluna de metadados `secoes_recuperadas` na saída CSV.
2. **Impacto de Avaliação:** A ausência dessa marcação estrutural faz com que os testes formais de seção computem revocação e precisão zeradas. Contudo, isso **não** afeta o conteúdo textual recuperado. O **Context Recall** geral avaliado pelo juiz atesta que a informação de contexto requerida é efetivamente entregue ao modelo para formulação da resposta.

---