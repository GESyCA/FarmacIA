# Comparação Intramodelo - MediPhi Instruct (ollama:mediphi-instruct)

Este relatório compara de forma objetiva o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG** na recuperação e na geração de respostas, além de reportar os tempos médios de execução obtidos com o modelo **MediPhi Instruct**.

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
| Naive RAG | 0.6973 | 40.0% | 0.8933 | 0.6267 | 0.1222 | 0.1963 | 0.1548 | 0.0000 | 0.0000 | 0.2281 | 0.0371 | 0.06s | 43.37s |
| Standard RAG | 0.6118 | 73.3% | 0.7067 | 0.5733 | 0.1111 | 0.1407 | 0.1137 | 0.6667 | 0.2778 | 0.2256 | 0.0573 | 2.55s | 4.24s |
| Agentic RAG | 0.5673 | 80.0% | 0.6267 | 0.5067 | 0.0778 | 0.0852 | 0.0785 | 0.4667 | 0.2667 | 0.1665 | 0.0170 | 2.59s | 4.12s |
| Hybrid Agent RAG | 0.4958 | 93.3% | 0.3333 | 0.3200 | 0.0333 | 0.0333 | 0.0333 | 0.1333 | 0.0667 | 0.0943 | 0.0055 | 2.81s | 45.83s |
| Fusion RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1077 | 0.0000 | 4.00s | **1.13s** |
| Graph RAG | 0.7212 | 46.7% | 0.7867 | 0.6667 | 0.1630 | 0.1963 | 0.1676 | 0.6000 | **0.4522** | 0.2310 | 0.0492 | **0.04s** | 9.21s |
| Guarded RAG | **0.8367** | **20.0%** | **0.9067** | **0.8267** | **0.2037** | **0.2481** | **0.2767** | **0.8667** | 0.2146 | **0.3460** | **0.1128** | 10.59s | 13.06s |

### Perguntas Médias (Medium)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7270 | 40.0% | 0.9467 | 0.7200 | 0.1259 | 0.2296 | 0.1319 | 0.0000 | 0.0000 | 0.2799 | 0.0735 | 0.07s | 55.58s |
| Standard RAG | 0.5555 | 80.0% | 0.7067 | 0.6267 | 0.1222 | 0.1444 | 0.1630 | 0.6222 | **0.4111** | 0.2170 | 0.0357 | 3.38s | 5.33s |
| Agentic RAG | 0.4488 | 80.0% | 0.6267 | 0.5600 | 0.0852 | 0.1296 | 0.1407 | 0.3889 | 0.3333 | 0.2038 | 0.0185 | 2.58s | 5.55s |
| Hybrid Agent RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0296 | 0.0667 | 0.0574 | 0.2556 | 0.2333 | 0.1314 | 0.0105 | 2.84s | 77.59s |
| Fusion RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1800 | 0.0042 | 5.21s | **2.01s** |
| Graph RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0778 | 0.1444 | 0.1361 | 0.3222 | 0.3000 | 0.2569 | 0.0806 | **0.06s** | 12.52s |
| Guarded RAG | **0.7300** | **33.3%** | **1.0000** | **0.8000** | **0.2259** | **0.2370** | **0.2333** | **0.7778** | 0.3783 | **0.2855** | **0.0827** | 30.39s | 263.41s |

### Perguntas Difáceis (Hard)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.5742 | **60.0%** | **1.0000** | 0.6133 | 0.0778 | 0.1722 | 0.1211 | 0.0000 | 0.0000 | 0.1963 | 0.0280 | 0.07s | 456.57s |
| Standard RAG | 0.4794 | 86.7% | 0.4133 | 0.5067 | 0.1204 | 0.1463 | 0.1504 | **0.7611** | **0.6222** | 0.2081 | 0.0183 | 3.24s | **7.13s** |
| Agentic RAG | 0.4079 | 93.3% | 0.5467 | 0.5200 | 0.0852 | 0.1074 | 0.1532 | 0.4222 | 0.5667 | 0.1935 | 0.0200 | 2.61s | 14.89s |
| Hybrid Agent RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0444 | 0.0593 | 0.0476 | 0.2167 | 0.2000 | 0.1753 | 0.0135 | 2.56s | 25.34s |
| Fusion RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1888 | 0.0128 | 17.49s | 10.62s |
| Graph RAG | 0.5485 | 73.3% | 0.7200 | 0.6000 | 0.0759 | 0.1444 | 0.1054 | 0.3500 | 0.2833 | 0.2010 | 0.0346 | **0.06s** | 19.37s |
| Guarded RAG | **0.6776** | 66.7% | 0.9600 | **0.8000** | **0.1852** | **0.2241** | **0.2415** | 0.7000 | 0.3475 | **0.2677** | **0.0730** | 17.21s | 24.49s |

---

## 2. Comparativo Consolidado por Pipeline (Média Geral)

A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline, unindo todas as dificuldades de perguntas:

| Pipeline | Média Final Score | Média Falhas Críticas | Média Chunk Recall@3 | Média Chunk Recall@10 | Média Chunk MRR@10 | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.6662 | 46.7% | 0.1086 | 0.1994 | 0.1359 | 0.9467 | 0.6533 | 0.2348 | 0.0462 | 0.07s | 185.17s |
| Standard RAG | 0.5489 | 80.0% | 0.1179 | 0.1438 | 0.1423 | 0.6089 | 0.5689 | 0.2169 | 0.0371 | 3.06s | 5.57s |
| Agentic RAG | 0.4746 | 84.4% | 0.0827 | 0.1074 | 0.1241 | 0.6000 | 0.5289 | 0.1879 | 0.0185 | 2.59s | 8.18s |
| Hybrid Agent RAG | 0.4958 | 93.3% | 0.0358 | 0.0531 | 0.0461 | 0.3333 | 0.3200 | 0.1337 | 0.0098 | 2.74s | 49.59s |
| Fusion RAG | 0.0000 | **0.0%** | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.1588 | 0.0057 | 8.90s | **4.59s** |
| Graph RAG | 0.6348 | 60.0% | 0.1056 | 0.1617 | 0.1364 | 0.7533 | 0.6333 | 0.2296 | 0.0548 | **0.06s** | 13.70s |
| Guarded RAG | **0.7481** | 40.0% | **0.2049** | **0.2364** | **0.2505** | **0.9556** | **0.8089** | **0.2998** | **0.0895** | 19.40s | 100.32s |

---

## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge

Detalhamento das médias obtidas em cada um dos **11 critérios individuais** avaliados pelo juiz (escala de 0.0 a 1.0):

### Critérios - Perguntas Fáceis (Easy)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8933 | 0.6267 | **0.8667** | 0.7600 | 0.7067 | 0.5000 | 0.6833 | 0.6333 | 0.5500 | 0.8000 | 0.6500 |
| Standard RAG | 0.7067 | 0.5733 | 0.6333 | 0.7867 | 0.6133 | 0.3000 | 0.6667 | 0.5833 | 0.5167 | 0.7333 | 0.6167 |
| Agentic RAG | 0.6267 | 0.5067 | 0.5167 | 0.7333 | 0.5733 | 0.2500 | 0.6833 | 0.5667 | 0.5167 | 0.6500 | 0.6167 |
| Hybrid Agent RAG | 0.3333 | 0.3200 | 0.1667 | 0.8267 | 0.4400 | 0.1000 | 0.7500 | 0.6333 | 0.3833 | 0.7667 | 0.7333 |
| Fusion RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Graph RAG | 0.7867 | 0.6667 | 0.7333 | **0.8800** | 0.7333 | 0.5167 | 0.7500 | 0.6833 | 0.6167 | 0.8333 | 0.7333 |
| Guarded RAG | **0.9067** | **0.8267** | **0.8667** | **0.8800** | **0.9067** | **0.7167** | **0.8667** | **0.7500** | **0.7333** | **0.8833** | **0.8667** |

### Critérios - Perguntas Médias (Medium)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.9467 | 0.7200 | 0.9167 | **0.7733** | 0.7067 | **0.5000** | **0.6833** | **0.7167** | **0.6833** | 0.7167 | **0.6333** |
| Standard RAG | 0.7067 | 0.6267 | 0.6333 | 0.6267 | 0.6000 | 0.3000 | 0.4833 | 0.4833 | 0.4333 | **0.7500** | 0.4667 |
| Agentic RAG | 0.6267 | 0.5600 | 0.5333 | 0.4933 | 0.5067 | 0.2000 | 0.3333 | 0.4000 | 0.3333 | 0.6333 | 0.3167 |
| Hybrid Agent RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Fusion RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Graph RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Guarded RAG | **1.0000** | **0.8000** | **1.0000** | 0.7467 | **0.7333** | **0.5000** | **0.6833** | 0.6500 | 0.5833 | 0.7000 | **0.6333** |

### Critérios - Perguntas Difáceis (Hard)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **1.0000** | 0.6133 | **1.0000** | 0.5600 | 0.6267 | 0.3500 | 0.3667 | 0.4833 | 0.3500 | 0.6000 | 0.3667 |
| Standard RAG | 0.4133 | 0.5067 | 0.2667 | 0.6533 | 0.5333 | 0.1667 | 0.5500 | 0.5167 | 0.4333 | **0.7167** | **0.5167** |
| Agentic RAG | 0.5467 | 0.5200 | 0.4500 | 0.4933 | 0.4933 | 0.1833 | 0.3500 | 0.3500 | 0.2333 | 0.5333 | 0.3333 |
| Hybrid Agent RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Fusion RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Graph RAG | 0.7200 | 0.6000 | 0.6500 | 0.6000 | 0.6800 | 0.3833 | 0.3833 | 0.5167 | 0.4333 | 0.6833 | 0.3833 |
| Guarded RAG | 0.9600 | **0.8000** | 0.9500 | **0.7200** | **0.7067** | **0.4167** | **0.6000** | **0.5833** | **0.5000** | 0.7000 | **0.5167** |

### Critérios - Média Geral (Consolidado de Todas as Dificuldades)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.9467 | 0.6533 | 0.9278 | 0.6978 | 0.6800 | 0.4500 | 0.5778 | 0.6111 | 0.5278 | 0.7056 | 0.5500 |
| Standard RAG | 0.6089 | 0.5689 | 0.5111 | 0.6889 | 0.5822 | 0.2556 | 0.5667 | 0.5278 | 0.4611 | 0.7333 | 0.5333 |
| Agentic RAG | 0.6000 | 0.5289 | 0.5000 | 0.5733 | 0.5244 | 0.2111 | 0.4556 | 0.4389 | 0.3611 | 0.6056 | 0.4222 |
| Hybrid Agent RAG | 0.3333 | 0.3200 | 0.1667 | **0.8267** | 0.4400 | 0.1000 | **0.7500** | 0.6333 | 0.3833 | **0.7667** | **0.7333** |
| Fusion RAG | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Graph RAG | 0.7533 | 0.6333 | 0.6917 | 0.7400 | 0.7067 | 0.4500 | 0.5667 | 0.6000 | 0.5250 | 0.7583 | 0.5583 |
| Guarded RAG | **0.9556** | **0.8089** | **0.9389** | 0.7822 | **0.7822** | **0.5444** | 0.7167 | **0.6611** | **0.6056** | 0.7611 | 0.6722 |

---

## 4. Notas Técnicas sobre o Pipeline "Naive RAG"

O **Naive RAG** apresenta valor `0.0000` em **Section Recall** e **Section Precision**.

### Explicação Técnica:
1. **Indexação Direta:** O Naive RAG fatia e indexa os textos de forma sequencial pura, sem estruturar o banco de dados vetorial por seções lógicas da bula (como fazem os outros pipelines). Por isso, ele não preenche a coluna de metadados `secoes_recuperadas` na saída CSV.
2. **Impacto de Avaliação:** A ausência dessa marcação estrutural faz com que os testes formais de seção computem revocação e precisão zeradas. Contudo, isso **não** afeta o conteúdo textual recuperado. O **Context Recall** geral avaliado pelo juiz atesta que a informação de contexto requerida é efetivamente entregue ao modelo para formulação da resposta.

---