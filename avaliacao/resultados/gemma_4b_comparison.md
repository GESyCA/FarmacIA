# Comparação Intramodelo - Gemma 4:4b (ollama:gemma4:e4b)

Este relatório compara de forma objetiva o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG** na recuperação e na geração de respostas, além de reportar os tempos médios de execução obtidos com o modelo **Gemma 4:4b**.

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
| Naive RAG | 0.9054 | 20.0% | **1.0000** | 0.7600 | 0.1185 | 0.1556 | 0.1106 | 0.0000 | 0.0000 | 0.3957 | 0.1680 | 0.04s | 19.94s |
| Standard RAG | 0.8991 | 6.7% | 0.9467 | 0.6933 | 0.1556 | 0.2074 | 0.1870 | **1.0000** | 0.5000 | 0.4110 | 0.1743 | 17.53s | 20.64s |
| Agentic RAG | 0.8718 | 13.3% | 0.8933 | 0.7067 | 0.1333 | 0.1852 | 0.1811 | 0.9333 | 0.8667 | 0.3982 | 0.1653 | 18.05s | 16.17s |
| Hybrid Agent RAG | 0.9215 | 6.7% | 0.9333 | 0.7733 | 0.1556 | 0.2074 | 0.2044 | **1.0000** | **1.0000** | **0.4355** | **0.1893** | 15.22s | 16.75s |
| Fusion RAG | 0.9400 | 6.7% | 0.9333 | **0.8800** | 0.1481 | 0.1481 | 0.1815 | 0.9333 | 0.7000 | 0.4052 | 0.1699 | 15.66s | **10.88s** |
| Graph RAG | 0.8155 | 26.7% | 0.8267 | 0.7200 | 0.1407 | 0.1741 | 0.1630 | 0.7333 | 0.4967 | 0.3109 | 0.1063 | **0.02s** | 16.51s |
| Guarded RAG | **0.9458** | **0.0%** | 0.9467 | 0.8667 | **0.1778** | **0.2222** | **0.2185** | **1.0000** | 0.1948 | 0.4310 | 0.1816 | 111.73s | 56.21s |

### Perguntas Médias (Medium)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **0.8948** | 20.0% | **1.0000** | **0.8000** | 0.0519 | 0.1407 | 0.0782 | 0.0000 | 0.0000 | **0.4239** | **0.1945** | 0.06s | 22.59s |
| Standard RAG | 0.8579 | **13.3%** | 0.8533 | 0.6933 | 0.0963 | **0.1481** | 0.1296 | 0.8111 | 0.6444 | 0.4188 | 0.1814 | 20.12s | 21.74s |
| Agentic RAG | 0.8000 | 26.7% | 0.7867 | 0.7467 | 0.0667 | 0.1296 | 0.1019 | 0.6111 | 0.6111 | 0.3893 | 0.1556 | 33.08s | 25.16s |
| Hybrid Agent RAG | 0.8721 | 20.0% | 0.8667 | **0.8000** | 0.0963 | **0.1481** | 0.1467 | 0.7111 | **0.7556** | 0.4186 | 0.1756 | 23.77s | 24.53s |
| Fusion RAG | 0.8076 | 33.3% | 0.8267 | 0.6800 | **0.1259** | 0.1259 | **0.1889** | 0.6444 | 0.4722 | 0.3867 | 0.1578 | 21.39s | **18.11s** |
| Graph RAG | 0.6545 | 60.0% | 0.6267 | 0.5467 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | **0.04s** | 20.57s |
| Guarded RAG | 0.8542 | 20.0% | 0.9467 | 0.7600 | **0.1259** | **0.1481** | 0.1722 | **0.9444** | 0.3981 | 0.4140 | 0.1637 | 89.21s | 46.93s |

### Perguntas Difáceis (Hard)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Chunk Recall@3 | Chunk Recall@10 | Chunk MRR@10 | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8476 | 33.3% | **1.0000** | 0.7867 | 0.0222 | 0.1204 | 0.0623 | 0.0000 | 0.0000 | 0.3652 | 0.1529 | 0.05s | 29.65s |
| Standard RAG | 0.8012 | 26.7% | 0.8800 | 0.7467 | 0.1037 | 0.1630 | 0.1611 | 0.7167 | **0.7889** | 0.3684 | 0.1661 | 32.30s | 30.81s |
| Agentic RAG | 0.8785 | 20.0% | 0.9867 | 0.8000 | 0.0889 | **0.1833** | 0.1404 | 0.8167 | 0.6733 | **0.4144** | **0.1786** | 27.84s | 30.31s |
| Hybrid Agent RAG | **0.8794** | **6.7%** | **1.0000** | 0.7733 | 0.0815 | 0.1796 | 0.1417 | 0.8278 | 0.7267 | 0.3729 | 0.1572 | 26.36s | 32.74s |
| Fusion RAG | 0.8149 | 26.7% | 0.8267 | 0.7067 | **0.1093** | 0.1259 | **0.1685** | 0.6278 | 0.5667 | 0.3543 | 0.1651 | 24.42s | **24.69s** |
| Graph RAG | 0.7185 | 46.7% | 0.7200 | 0.6400 | 0.0407 | 0.1074 | 0.0904 | 0.5111 | 0.4167 | 0.2483 | 0.0842 | **0.02s** | 26.78s |
| Guarded RAG | 0.8512 | 13.3% | 0.9467 | **0.8800** | **0.1093** | 0.1333 | 0.1415 | **0.9222** | 0.4152 | 0.3483 | 0.1311 | 38.22s | 29.85s |

---

## 2. Comparativo Consolidado por Pipeline (Média Geral)

A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline, unindo todas as dificuldades de perguntas:

| Pipeline | Média Final Score | Média Falhas Críticas | Média Chunk Recall@3 | Média Chunk Recall@10 | Média Chunk MRR@10 | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8826 | 24.4% | 0.0642 | 0.1389 | 0.0837 | **1.0000** | 0.7822 | 0.3950 | 0.1718 | 0.05s | 24.06s |
| Standard RAG | 0.8527 | 15.6% | 0.1185 | 0.1728 | 0.1593 | 0.8933 | 0.7111 | 0.3994 | 0.1739 | 23.32s | 24.40s |
| Agentic RAG | 0.8501 | 20.0% | 0.0963 | 0.1660 | 0.1411 | 0.8889 | 0.7511 | 0.4006 | 0.1665 | 26.32s | 23.88s |
| Hybrid Agent RAG | **0.8910** | **11.1%** | 0.1111 | **0.1784** | 0.1643 | 0.9333 | 0.7822 | **0.4090** | **0.1740** | 21.79s | 24.67s |
| Fusion RAG | 0.8541 | 22.2% | 0.1278 | 0.1333 | **0.1796** | 0.8622 | 0.7556 | 0.3821 | 0.1643 | 20.49s | **17.89s** |
| Graph RAG | 0.7295 | 44.4% | 0.0605 | 0.0938 | 0.0844 | 0.7244 | 0.6356 | 0.1864 | 0.0635 | **0.03s** | 21.29s |
| Guarded RAG | 0.8837 | **11.1%** | **0.1377** | 0.1679 | 0.1774 | 0.9467 | **0.8356** | 0.3978 | 0.1588 | 79.72s | 44.33s |

---

## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge

Detalhamento das médias obtidas em cada um dos **11 critérios individuais** avaliados pelo juiz (escala de 0.0 a 1.0):

### Critérios - Perguntas Fáceis (Easy)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **1.0000** | 0.7600 | **1.0000** | 0.9467 | 0.8533 | 0.8167 | 0.9333 | 0.9333 | 0.9167 | 0.8833 | 0.9167 |
| Standard RAG | 0.9467 | 0.6933 | 0.9333 | 0.9600 | 0.9067 | 0.9000 | 0.9667 | 0.9333 | 0.9000 | 0.8000 | 0.9500 |
| Agentic RAG | 0.8933 | 0.7067 | 0.8667 | 0.9600 | 0.8800 | 0.8167 | 0.9167 | 0.8833 | 0.8500 | 0.9000 | 0.9167 |
| Hybrid Agent RAG | 0.9333 | 0.7733 | 0.9000 | 0.9600 | 0.9200 | 0.9167 | 0.9667 | 0.9500 | **0.9333** | **0.9333** | 0.9500 |
| Fusion RAG | 0.9333 | **0.8800** | 0.9167 | **0.9867** | 0.9067 | 0.9333 | **1.0000** | **0.9667** | **0.9333** | 0.9000 | **0.9833** |
| Graph RAG | 0.8267 | 0.7200 | 0.7667 | 0.9200 | 0.7867 | 0.7167 | 0.9333 | 0.8333 | 0.7167 | 0.8667 | 0.8833 |
| Guarded RAG | 0.9467 | 0.8667 | 0.9500 | 0.9733 | **1.0000** | **0.9667** | 0.9667 | 0.9333 | 0.9167 | 0.9167 | 0.9667 |

### Critérios - Perguntas Médias (Medium)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **1.0000** | **0.8000** | **1.0000** | 0.9867 | 0.8400 | 0.7000 | **1.0000** | **0.9333** | **0.8000** | 0.9167 | 0.8667 |
| Standard RAG | 0.8533 | 0.6933 | 0.8167 | **1.0000** | 0.8400 | 0.6833 | **1.0000** | 0.8833 | 0.7667 | **0.9667** | 0.9333 |
| Agentic RAG | 0.7867 | 0.7467 | 0.7333 | 0.9200 | 0.8133 | 0.5500 | 0.9667 | 0.8167 | 0.6333 | 0.9500 | 0.8833 |
| Hybrid Agent RAG | 0.8667 | **0.8000** | 0.8333 | 0.9600 | **0.8667** | **0.7333** | 0.9667 | 0.8833 | 0.7667 | 0.9500 | **0.9667** |
| Fusion RAG | 0.8267 | 0.6800 | 0.7833 | 0.9333 | 0.7600 | 0.5167 | **1.0000** | 0.9000 | 0.7167 | 0.9333 | 0.8333 |
| Graph RAG | 0.6267 | 0.5467 | 0.5333 | 0.8400 | 0.5867 | 0.4000 | 0.9167 | 0.7333 | 0.4333 | 0.8333 | 0.7500 |
| Guarded RAG | 0.9467 | 0.7600 | 0.9333 | 0.8933 | 0.8133 | 0.6333 | 0.8833 | 0.8833 | **0.8000** | **0.9667** | 0.8833 |

### Critérios - Perguntas Difáceis (Hard)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **1.0000** | 0.7867 | **1.0000** | 0.9200 | 0.8000 | 0.6167 | **0.9833** | 0.8667 | 0.7167 | 0.7833 | 0.8500 |
| Standard RAG | 0.8800 | 0.7467 | 0.8500 | 0.9067 | 0.8133 | 0.6000 | 0.8667 | 0.8500 | 0.7167 | 0.8667 | 0.7167 |
| Agentic RAG | 0.9867 | 0.8000 | 0.9833 | 0.9067 | 0.9200 | 0.7167 | 0.8833 | **0.9167** | 0.7500 | **0.9833** | 0.8167 |
| Hybrid Agent RAG | **1.0000** | 0.7733 | **1.0000** | 0.9067 | **0.9600** | **0.7667** | 0.8833 | **0.9167** | **0.8500** | 0.7667 | 0.8500 |
| Fusion RAG | 0.8267 | 0.7067 | 0.7667 | **0.9600** | 0.7867 | 0.5833 | **0.9833** | 0.8667 | 0.6833 | 0.9000 | **0.9000** |
| Graph RAG | 0.7200 | 0.6400 | 0.6500 | 0.9067 | 0.6533 | 0.4667 | 0.9667 | 0.7667 | 0.5500 | 0.7667 | 0.8167 |
| Guarded RAG | 0.9467 | **0.8800** | 0.9167 | 0.8800 | 0.8400 | 0.6333 | 0.9000 | 0.8667 | 0.7833 | 0.9667 | 0.7500 |

### Critérios - Média Geral (Consolidado de Todas as Dificuldades)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | **1.0000** | 0.7822 | **1.0000** | 0.9511 | 0.8311 | 0.7111 | 0.9722 | 0.9111 | 0.8111 | 0.8611 | 0.8778 |
| Standard RAG | 0.8933 | 0.7111 | 0.8667 | 0.9556 | 0.8533 | 0.7278 | 0.9444 | 0.8889 | 0.7944 | 0.8778 | 0.8667 |
| Agentic RAG | 0.8889 | 0.7511 | 0.8611 | 0.9289 | 0.8711 | 0.6944 | 0.9222 | 0.8722 | 0.7444 | 0.9444 | 0.8722 |
| Hybrid Agent RAG | 0.9333 | 0.7822 | 0.9111 | 0.9422 | **0.9156** | **0.8056** | 0.9389 | **0.9167** | **0.8500** | 0.8833 | **0.9222** |
| Fusion RAG | 0.8622 | 0.7556 | 0.8222 | **0.9600** | 0.8178 | 0.6778 | **0.9944** | 0.9111 | 0.7778 | 0.9111 | 0.9056 |
| Graph RAG | 0.7244 | 0.6356 | 0.6500 | 0.8889 | 0.6756 | 0.5278 | 0.9389 | 0.7778 | 0.5667 | 0.8222 | 0.8167 |
| Guarded RAG | 0.9467 | **0.8356** | 0.9333 | 0.9156 | 0.8844 | 0.7444 | 0.9167 | 0.8944 | 0.8333 | **0.9500** | 0.8667 |

---

## 4. Notas Técnicas sobre o Pipeline "Naive RAG"

O **Naive RAG** apresenta valor `0.0000` em **Section Recall** e **Section Precision**.

### Explicação Técnica:
1. **Indexação Direta:** O Naive RAG fatia e indexa os textos de forma sequencial pura, sem estruturar o banco de dados vetorial por seções lógicas da bula (como fazem os outros pipelines). Por isso, ele não preenche a coluna de metadados `secoes_recuperadas` na saída CSV.
2. **Impacto de Avaliação:** A ausência dessa marcação estrutural faz com que os testes formais de seção computem revocação e precisão zeradas. Contudo, isso **não** afeta o conteúdo textual recuperado. O **Context Recall** geral avaliado pelo juiz atesta que a informação de contexto requerida é efetivamente entregue ao modelo para formulação da resposta.

---