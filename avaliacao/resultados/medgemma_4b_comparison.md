# Comparação Intramodelo - MedGemma 4b (ollama:medgemma:4b)

Este relatório compara de forma objetiva o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG** na recuperação e na geração de respostas, além de reportar os tempos médios de execução obtidos com o modelo **MedGemma 4b**.

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
| Naive RAG | 0.8064 | 40.0% | 0.9067 | **0.8800** | 0.1185 | 0.1556 | 0.1106 | 0.0000 | 0.0000 | 0.3741 | 0.1432 | **0.03s** | 19.19s |
| Standard RAG | 0.8318 | 53.3% | **0.9733** | 0.4667 | 0.1185 | 0.1963 | 0.1525 | 0.9333 | 0.4333 | 0.3849 | 0.1408 | 2.94s | 6.90s |
| Agentic RAG | 0.7585 | 53.3% | 0.9467 | 0.5333 | 0.1333 | 0.2074 | 0.1726 | 0.9333 | 0.6889 | 0.3778 | 0.1412 | 2.49s | **5.14s** |
| Hybrid Agent RAG | 0.8249 | 60.0% | 0.9467 | 0.4800 | 0.1333 | 0.1963 | 0.1861 | 0.9333 | **0.8000** | **0.3857** | **0.1489** | 2.72s | 6.39s |
| Fusion RAG | 0.7994 | 40.0% | 0.9467 | 0.7200 | 0.1481 | 0.1481 | 0.1815 | 0.9333 | 0.7000 | 0.3084 | 0.0983 | 4.94s | 34.03s |
| Graph RAG | 0.8152 | 26.7% | 0.9333 | 0.7867 | 0.1407 | 0.1741 | 0.1630 | 0.7333 | 0.4967 | 0.2735 | 0.0886 | 0.03s | 5.44s |
| Guarded RAG | **0.8939** | **20.0%** | **0.9733** | 0.7467 | **0.2111** | **0.2296** | **0.2185** | **1.0000** | 0.3800 | 0.3428 | 0.1351 | 10.73s | 37.32s |

### Perguntas Médias (Medium)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7276 | 46.7% | 0.8667 | 0.8133 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.03s | 19.27s |
| Standard RAG | 0.6603 | 100.0% | 0.9067 | 0.2400 | 0.0852 | 0.1519 | 0.1137 | 0.8444 | **0.5056** | 0.3373 | 0.1336 | 2.55s | 24.10s |
| Agentic RAG | 0.6127 | 100.0% | 0.7733 | 0.2000 | 0.0778 | 0.1185 | 0.0907 | 0.5111 | 0.4000 | 0.3245 | 0.1025 | 2.65s | 6.14s |
| Hybrid Agent RAG | 0.6391 | 100.0% | 0.7867 | 0.2133 | 0.0630 | 0.1370 | 0.0891 | 0.5556 | 0.4222 | 0.2736 | 0.0753 | 2.95s | 23.94s |
| Fusion RAG | 0.6233 | 80.0% | 0.7600 | 0.4133 | 0.1111 | 0.1111 | **0.2000** | 0.5889 | 0.3944 | 0.3370 | 0.1221 | 4.99s | **4.89s** |
| Graph RAG | 0.7094 | 60.0% | **0.9600** | **0.8933** | 0.0630 | 0.1074 | 0.1161 | 0.4556 | 0.3944 | 0.2429 | 0.0639 | **0.02s** | 6.68s |
| Guarded RAG | **0.8364** | **20.0%** | 0.9467 | 0.8267 | **0.1444** | **0.1556** | 0.1519 | **0.9222** | 0.4156 | **0.3787** | **0.1514** | 20.56s | 11.65s |

### Perguntas Difíceis (Hard)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.6812 | 60.0% | 0.8667 | 0.7067 | 0.0222 | 0.1204 | 0.0623 | 0.0000 | 0.0000 | 0.2766 | **0.1047** | **0.05s** | 28.38s |
| Standard RAG | 0.6564 | 100.0% | 0.8533 | 0.2267 | 0.0667 | 0.1556 | 0.1058 | **0.8611** | **0.6222** | **0.3052** | 0.1041 | 2.83s | 8.61s |
| Agentic RAG | 0.6358 | 100.0% | 0.8667 | 0.2267 | 0.0667 | **0.1574** | 0.0934 | 0.8222 | 0.6167 | 0.2530 | 0.0803 | 3.08s | 16.46s |
| Hybrid Agent RAG | 0.6576 | 100.0% | 0.8800 | 0.2400 | 0.0593 | 0.1500 | 0.0797 | 0.8389 | 0.5833 | 0.2494 | 0.0807 | 3.48s | 26.95s |
| Fusion RAG | 0.5991 | 93.3% | 0.7733 | 0.3333 | **0.1093** | 0.1222 | **0.1722** | 0.6611 | 0.4967 | 0.2965 | 0.0948 | 8.66s | **7.00s** |
| Graph RAG | 0.6706 | 60.0% | 0.8800 | 0.7600 | 0.0407 | 0.1074 | 0.0904 | 0.5111 | 0.4167 | 0.1726 | 0.0359 | 0.14s | 61.03s |
| Guarded RAG | **0.7545** | **46.7%** | **0.9733** | **0.8000** | 0.0889 | 0.1407 | 0.1637 | 0.8222 | 0.5033 | 0.2783 | 0.0958 | 17.40s | 52.74s |

---

## 2. Comparativo Consolidado por Pipeline (Média Geral)

A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline, unindo todas as dificuldades de perguntas:

| Pipeline | Média Final Score | Média Falhas Críticas | Média Chunk Recall@3 | Média Chunk Recall@10 | Média Chunk MRR@10 | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7384 | 48.9% | 0.0469 | 0.0920 | 0.0576 | 0.8800 | 0.8000 | 0.2169 | 0.0826 | **0.04s** | 22.28s |
| Standard RAG | 0.7162 | 84.4% | 0.0901 | 0.1679 | 0.1240 | 0.9111 | 0.3111 | **0.3425** | 0.1261 | 2.78s | 13.20s |
| Agentic RAG | 0.6690 | 84.4% | 0.0926 | 0.1611 | 0.1189 | 0.8622 | 0.3200 | 0.3185 | 0.1080 | 2.74s | **9.25s** |
| Hybrid Agent RAG | 0.7072 | 86.7% | 0.0852 | 0.1611 | 0.1183 | 0.8711 | 0.3111 | 0.3029 | 0.1016 | 3.05s | 19.09s |
| Fusion RAG | 0.6739 | 71.1% | 0.1228 | 0.1272 | **0.1846** | 0.8267 | 0.4889 | 0.3140 | 0.1050 | 6.20s | 15.31s |
| Graph RAG | 0.7317 | 48.9% | 0.0815 | 0.1296 | 0.1232 | 0.9244 | **0.8133** | 0.2297 | 0.0628 | 0.07s | 24.38s |
| Guarded RAG | **0.8283** | **28.9%** | **0.1481** | **0.1753** | 0.1780 | **0.9644** | 0.7911 | 0.3333 | **0.1275** | 16.23s | 33.90s |

---

## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge

Detalhamento das médias obtidas em cada um dos **11 critérios individuais** avaliados pelo juiz (escala de 0.0 a 1.0):

### Critérios - Perguntas Fáceis (Easy)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.9067 | **0.8800** | 0.8833 | 0.7600 | 0.7067 | 0.6167 | **1.0000** | 0.7833 | 0.6833 | 0.9500 | 0.7000 |
| Standard RAG | **0.9733** | 0.4667 | 0.9333 | 0.8533 | 0.7067 | 0.7667 | 0.8167 | **0.9833** | 0.8167 | **1.0000** | 0.8333 |
| Agentic RAG | 0.9467 | 0.5333 | 0.9167 | 0.7467 | 0.6667 | 0.6000 | 0.6833 | 0.9333 | 0.5667 | **1.0000** | 0.7500 |
| Hybrid Agent RAG | 0.9467 | 0.4800 | 0.9333 | 0.8133 | 0.7333 | **0.7833** | 0.7667 | **0.9833** | 0.8000 | **1.0000** | 0.8333 |
| Fusion RAG | 0.9467 | 0.7200 | 0.9167 | 0.7867 | 0.7067 | 0.6333 | 0.7333 | 0.9333 | 0.6500 | 0.9667 | 0.8000 |
| Graph RAG | 0.9333 | 0.7867 | 0.8500 | 0.8933 | 0.7867 | 0.7333 | 0.8500 | 0.7667 | **0.8333** | 0.7500 | 0.7833 |
| Guarded RAG | **0.9733** | 0.7467 | **0.9667** | **1.0000** | **0.8800** | **0.7833** | **1.0000** | 0.8500 | **0.8333** | 0.8500 | **0.9500** |

### Critérios - Perguntas Médias (Medium)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8667 | 0.8133 | 0.8333 | 0.6667 | 0.6400 | 0.4500 | **0.9667** | 0.7333 | 0.5167 | 0.9333 | 0.5833 |
| Standard RAG | 0.9067 | 0.2400 | 0.8167 | 0.7200 | 0.5467 | 0.4167 | 0.6500 | **0.7833** | 0.5167 | 0.9333 | 0.7333 |
| Agentic RAG | 0.7733 | 0.2000 | 0.6667 | 0.7200 | 0.5467 | 0.3333 | 0.6500 | 0.7000 | 0.4833 | 0.9667 | 0.7000 |
| Hybrid Agent RAG | 0.7867 | 0.2133 | 0.6667 | 0.7867 | 0.4933 | 0.3333 | 0.7167 | 0.7667 | 0.5500 | 0.9333 | **0.7833** |
| Fusion RAG | 0.7600 | 0.4133 | 0.6333 | 0.6800 | 0.5200 | 0.3667 | 0.5833 | 0.7000 | 0.5000 | **0.9833** | 0.7167 |
| Graph RAG | **0.9600** | **0.8933** | 0.9333 | 0.8400 | 0.4933 | 0.3667 | 0.7667 | 0.4833 | 0.6833 | 0.7167 | 0.6667 |
| Guarded RAG | 0.9467 | 0.8267 | **0.9500** | **0.9467** | **0.8133** | **0.6333** | 0.9167 | **0.7833** | **0.7667** | 0.9000 | 0.7167 |

### Critérios - Perguntas Difíceis (Hard)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8667 | 0.7067 | 0.7667 | 0.6400 | 0.6133 | 0.4333 | **0.9667** | 0.7167 | 0.4833 | 0.8167 | 0.4833 |
| Standard RAG | 0.8533 | 0.2267 | 0.7833 | 0.8000 | 0.5067 | 0.3667 | 0.7500 | **0.7500** | 0.5167 | 0.8833 | 0.7833 |
| Agentic RAG | 0.8667 | 0.2267 | 0.7667 | 0.8400 | 0.4267 | 0.3000 | 0.8167 | 0.6833 | 0.4333 | 0.7833 | **0.8500** |
| Hybrid Agent RAG | 0.8800 | 0.2400 | 0.8000 | 0.8533 | 0.4933 | 0.3333 | 0.7667 | 0.7167 | 0.4667 | 0.8500 | 0.8333 |
| Fusion RAG | 0.7733 | 0.3333 | 0.6333 | 0.7200 | 0.4800 | 0.3000 | 0.6167 | 0.7000 | 0.4167 | **0.9000** | 0.7167 |
| Graph RAG | 0.8800 | 0.7600 | 0.8333 | 0.9200 | 0.5333 | 0.4167 | 0.8667 | 0.4167 | 0.5833 | 0.6167 | 0.5500 |
| Guarded RAG | **0.9733** | **0.8000** | **0.9667** | **0.9600** | **0.6667** | **0.4667** | **0.9667** | 0.6667 | **0.6000** | 0.6167 | 0.6167 |

### Critérios - Média Geral (Consolidado de Todas as Dificuldades)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8800 | 0.8000 | 0.8278 | 0.6889 | 0.6533 | 0.5000 | **0.9778** | 0.7444 | 0.5611 | 0.9000 | 0.5889 |
| Standard RAG | 0.9111 | 0.3111 | 0.8444 | 0.7911 | 0.5867 | 0.5167 | 0.7389 | **0.8389** | 0.6167 | 0.9389 | 0.7833 |
| Agentic RAG | 0.8622 | 0.3200 | 0.7833 | 0.7689 | 0.5467 | 0.4111 | 0.7167 | 0.7722 | 0.4944 | 0.9167 | 0.7667 |
| Hybrid Agent RAG | 0.8711 | 0.3111 | 0.8000 | 0.8178 | 0.5733 | 0.4833 | 0.7500 | 0.8222 | 0.6056 | 0.9278 | **0.8167** |
| Fusion RAG | 0.8267 | 0.4889 | 0.7278 | 0.7289 | 0.5689 | 0.4333 | 0.6444 | 0.7778 | 0.5222 | **0.9500** | 0.7444 |
| Graph RAG | 0.9244 | **0.8133** | 0.8722 | 0.8844 | 0.6044 | 0.5056 | 0.8278 | 0.5556 | 0.7000 | 0.6944 | 0.6667 |
| Guarded RAG | **0.9644** | 0.7911 | **0.9611** | **0.9689** | **0.7867** | **0.6278** | 0.9611 | 0.7667 | **0.7333** | 0.7889 | 0.7611 |

---

## 4. Notas Técnicas sobre o Pipeline "Naive RAG"

O **Naive RAG** apresenta valor `0.0000` em **Section Recall** e **Section Precision**.

### Explicação Técnica:
1. **Indexação Direta:** O Naive RAG fatia e indexa os textos de forma sequencial pura, sem estruturar o banco de dados vetorial por seções lógicas da bula (como fazem os outros pipelines). Por isso, ele não preenche a coluna de metadados `secoes_recuperadas` na saída CSV.
2. **Impacto de Avaliação:** A ausência dessa marcação estrutural faz com que os testes formais de seção computem revocação e precisão zeradas. Contudo, isso **não** afeta o conteúdo textual recuperado. O **Context Recall** geral avaliado pelo juiz atesta que a informação de contexto requerida é efetivamente entregue ao modelo para formulação da resposta.

---