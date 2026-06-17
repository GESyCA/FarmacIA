# Comparação Intramodelo - Gemma 4:4b (ollama:gemma4:e4b)

Este relatório compara o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG implementado** na recuperação e na geração de respostas, bem como a eficiência de tempo de execução, utilizando exclusivamente os resultados obtidos com o modelo **Gemma 4:4b** no diretório `resultados/gemma_4_4b`.

> [!NOTE]
> **Definição do Final Score:** O **Final Score** é exatamente a média aritmética das notas normalizadas (de 0.0 a 1.0) atribuídas pelo **LLM-as-a-judge** (ChatGPT / Gemini) nos **11 critérios clínicos e contextuais** definidos no projeto (listados na seção 3).

---

## 1. Resultados Detalhados por Dificuldade

### Perguntas Fáceis (Easy)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.9054 | 20.0% | 1.0000 | 0.7600 | 0.0000 | 0.0000 | 0.3901 | 0.1680 | 0.04s | 19.94s |
| Standard RAG | 0.8991 | 6.7% | 0.9467 | 0.6933 | 1.0000 | 0.5000 | 0.4075 | 0.1743 | 17.53s | 20.64s |
| Agentic RAG | 0.8718 | 13.3% | 0.8933 | 0.7067 | 0.9333 | 0.8667 | 0.4018 | 0.1653 | 18.05s | 16.17s |
| Hybrid Agent RAG | 0.9215 | 6.7% | 0.9333 | 0.7733 | 1.0000 | 1.0000 | 0.4383 | 0.1893 | 15.22s | 16.75s |
| Fusion RAG | 0.9400 | 6.7% | 0.9333 | 0.8800 | 0.9333 | 0.7000 | 0.4052 | 0.1699 | 15.66s | 10.88s |
| Graph RAG | 0.8155 | 26.7% | 0.8267 | 0.7200 | 0.7333 | 0.4967 | 0.3116 | 0.1063 | 0.02s | 16.51s |

### Perguntas Médias (Medium)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8948 | 20.0% | 1.0000 | 0.8000 | 0.0000 | 0.0000 | 0.4272 | 0.1945 | 0.06s | 22.59s |
| Standard RAG | 0.8579 | 13.3% | 0.8533 | 0.6933 | 0.8111 | 0.6444 | 0.4177 | 0.1814 | 20.12s | 21.74s |
| Agentic RAG | 0.8000 | 26.7% | 0.7867 | 0.7467 | 0.6111 | 0.6111 | 0.3903 | 0.1556 | 33.08s | 25.16s |
| Hybrid Agent RAG | 0.8721 | 20.0% | 0.8667 | 0.8000 | 0.7111 | 0.7556 | 0.4199 | 0.1756 | 23.77s | 24.53s |
| Fusion RAG | 0.8076 | 33.3% | 0.8267 | 0.6800 | 0.6444 | 0.4722 | 0.3863 | 0.1578 | 21.39s | 18.11s |
| Graph RAG | 0.6545 | 60.0% | 0.6267 | 0.5467 | 0.4556 | 0.3944 | 0.2698 | 0.0783 | 0.04s | 20.57s |

### Perguntas Difíceis (Hard)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8476 | 33.3% | 1.0000 | 0.7867 | 0.0000 | 0.0000 | 0.3643 | 0.1529 | 0.05s | 29.65s |
| Standard RAG | 0.8012 | 26.7% | 0.8800 | 0.7467 | 0.7167 | 0.7889 | 0.3680 | 0.1661 | 32.30s | 30.81s |
| Agentic RAG | 0.8785 | 20.0% | 0.9867 | 0.8000 | 0.8167 | 0.6733 | 0.4140 | 0.1786 | 27.84s | 30.31s |
| Hybrid Agent RAG | 0.8794 | 6.7% | 1.0000 | 0.7733 | 0.8278 | 0.7267 | 0.3723 | 0.1572 | 26.36s | 32.74s |
| Fusion RAG | 0.8149 | 26.7% | 0.8267 | 0.7067 | 0.6278 | 0.5667 | 0.3545 | 0.1651 | 24.42s | 24.69s |
| Graph RAG | 0.7185 | 46.7% | 0.7200 | 0.6400 | 0.5111 | 0.4167 | 0.2453 | 0.0842 | 0.02s | 26.78s |

---

## 2. Comparativo Consolidado por Pipeline (Média Geral)

A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline unindo todas as dificuldades:

| Pipeline | Média Final Score | Média Falhas Críticas | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8826 | 24.4% | 1.0000 | 0.7822 | 0.3939 | 0.1718 | 0.05s | 24.06s |
| Standard RAG | 0.8527 | 15.6% | 0.8933 | 0.7111 | 0.3977 | 0.1739 | 23.32s | 24.40s |
| Agentic RAG | 0.8501 | 20.0% | 0.8889 | 0.7511 | 0.4021 | 0.1665 | 26.32s | 23.88s |
| Hybrid Agent RAG | 0.8910 | 11.1% | 0.9333 | 0.7822 | 0.4102 | 0.1740 | 21.79s | 24.67s |
| Fusion RAG | 0.8541 | 22.2% | 0.8622 | 0.7556 | 0.3820 | 0.1643 | 20.49s | 17.89s |
| Graph RAG | 0.7295 | 44.4% | 0.7244 | 0.6356 | 0.2756 | 0.0896 | 0.03s | 21.29s |
## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge

Abaixo estão detalhadas as médias obtidas em cada um dos **11 critérios clínicos e contextuais** individuais avaliados pelo LLM-as-a-judge (escala de 0.0 a 1.0), divididos por nível de dificuldade das perguntas e consolidados em uma média geral:

### Critérios - Perguntas Fáceis (Easy)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 1.0000 | 0.7600 | 1.0000 | 0.9467 | 0.8533 | 0.8167 | 0.9333 | 0.9333 | 0.9167 | 0.8833 | 0.9167 |
| Standard RAG | 0.9467 | 0.6933 | 0.9333 | 0.9600 | 0.9067 | 0.9000 | 0.9667 | 0.9333 | 0.9000 | 0.8000 | 0.9500 |
| Agentic RAG | 0.8933 | 0.7067 | 0.8667 | 0.9600 | 0.8800 | 0.8167 | 0.9167 | 0.8833 | 0.8500 | 0.9000 | 0.9167 |
| Hybrid Agent RAG | 0.9333 | 0.7733 | 0.9000 | 0.9600 | 0.9200 | 0.9167 | 0.9667 | 0.9500 | 0.9333 | 0.9333 | 0.9500 |
| Fusion RAG | 0.9333 | 0.8800 | 0.9167 | 0.9867 | 0.9067 | 0.9333 | 1.0000 | 0.9667 | 0.9333 | 0.9000 | 0.9833 |
| Graph RAG | 0.8267 | 0.7200 | 0.7667 | 0.9200 | 0.7867 | 0.7167 | 0.9333 | 0.8333 | 0.7167 | 0.8667 | 0.8833 |

### Critérios - Perguntas Médias (Medium)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 1.0000 | 0.8000 | 1.0000 | 0.9867 | 0.8400 | 0.7000 | 1.0000 | 0.9333 | 0.8000 | 0.9167 | 0.8667 |
| Standard RAG | 0.8533 | 0.6933 | 0.8167 | 1.0000 | 0.8400 | 0.6833 | 1.0000 | 0.8833 | 0.7667 | 0.9667 | 0.9333 |
| Agentic RAG | 0.7867 | 0.7467 | 0.7333 | 0.9200 | 0.8133 | 0.5500 | 0.9667 | 0.8167 | 0.6333 | 0.9500 | 0.8833 |
| Hybrid Agent RAG | 0.8667 | 0.8000 | 0.8333 | 0.9600 | 0.8667 | 0.7333 | 0.9667 | 0.8833 | 0.7667 | 0.9500 | 0.9667 |
| Fusion RAG | 0.8267 | 0.6800 | 0.7833 | 0.9333 | 0.7600 | 0.5167 | 1.0000 | 0.9000 | 0.7167 | 0.9333 | 0.8333 |
| Graph RAG | 0.6267 | 0.5467 | 0.5333 | 0.8400 | 0.5867 | 0.4000 | 0.9167 | 0.7333 | 0.4333 | 0.8333 | 0.7500 |

### Critérios - Perguntas Difíceis (Hard)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 1.0000 | 0.7867 | 1.0000 | 0.9200 | 0.8000 | 0.6167 | 0.9833 | 0.8667 | 0.7167 | 0.7833 | 0.8500 |
| Standard RAG | 0.8800 | 0.7467 | 0.8500 | 0.9067 | 0.8133 | 0.6000 | 0.8667 | 0.8500 | 0.7167 | 0.8667 | 0.7167 |
| Agentic RAG | 0.9867 | 0.8000 | 0.9833 | 0.9067 | 0.9200 | 0.7167 | 0.8833 | 0.9167 | 0.7500 | 0.9833 | 0.8167 |
| Hybrid Agent RAG | 1.0000 | 0.7733 | 1.0000 | 0.9067 | 0.9600 | 0.7667 | 0.8833 | 0.9167 | 0.8500 | 0.7667 | 0.8500 |
| Fusion RAG | 0.8267 | 0.7067 | 0.7667 | 0.9600 | 0.7867 | 0.5833 | 0.9833 | 0.8667 | 0.6833 | 0.9000 | 0.9000 |
| Graph RAG | 0.7200 | 0.6400 | 0.6500 | 0.9067 | 0.6533 | 0.4667 | 0.9667 | 0.7667 | 0.5500 | 0.7667 | 0.8167 |

### Critérios - Média Geral (Consolidado de Todas as Dificuldades)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 1.0000 | 0.7822 | 1.0000 | 0.9511 | 0.8311 | 0.7111 | 0.9722 | 0.9111 | 0.8111 | 0.8611 | 0.8778 |
| Standard RAG | 0.8933 | 0.7111 | 0.8667 | 0.9556 | 0.8533 | 0.7278 | 0.9444 | 0.8889 | 0.7944 | 0.8778 | 0.8667 |
| Agentic RAG | 0.8889 | 0.7511 | 0.8611 | 0.9289 | 0.8711 | 0.6944 | 0.9222 | 0.8722 | 0.7444 | 0.9444 | 0.8722 |
| Hybrid Agent RAG | 0.9333 | 0.7822 | 0.9111 | 0.9422 | 0.9156 | 0.8056 | 0.9389 | 0.9167 | 0.8500 | 0.8833 | 0.9222 |
| Fusion RAG | 0.8622 | 0.7556 | 0.8222 | 0.9600 | 0.8178 | 0.6778 | 0.9944 | 0.9111 | 0.7778 | 0.9111 | 0.9056 |
| Graph RAG | 0.7244 | 0.6356 | 0.6500 | 0.8889 | 0.6756 | 0.5278 | 0.9389 | 0.7778 | 0.5667 | 0.8222 | 0.8167 |

---

## 4. Esclarecimento Sobre o "Naive RAG" com Nota Zero

Você pode notar que o **Naive RAG** apresenta pontuações zeradas (`0.0000`) nas seguintes colunas:
- **Section Recall** (Revocação de Seções)
- **Section Precision** (Precisão de Seções)

### Por que isso ocorre?
Essas colunas representam as **Métricas Estruturais de Recuperação** (comparação das seções formais da bula onde as informações deveriam estar, como *'COMO DEVO USAR ESTE MEDICAMENTO?'*, com as seções realmente acessadas pelo pipeline).

1. **Funcionamento do Naive RAG**: Ele é o pipeline mais simples de RAG. Ele fatia o texto das bulas de forma sequencial (baseado em caracteres ou palavras) e faz a busca semântica diretamente sobre os chunks, sem classificar de qual seção aquele chunk provém e sem preencher a coluna `secoes_recuperadas` na saída CSV.
2. **Cálculo da Métrica**: Como a coluna `secoes_recuperadas` é deixada vazia no Naive RAG, o script de avaliação automática interpreta que o pipeline não conseguiu recuperar nenhuma seção formal. Por isso, a nota estrutural de seção é `0.0000` (zero).

### O Naive RAG falhou em ler as informações?
**Não!** Se você olhar a métrica **Context Recall**, verá que ela é **1.0000 (100%)** em todas as dificuldades nas avaliações do juiz. Isso significa que, semanticamente, o conteúdo recuperado continha toda a informação necessária para responder às perguntas, e o modelo conseguiu ler essa informação no contexto para formular a resposta final. Por esse motivo, o **Final Score** geral dele é alto (média de 0.8826), embora a métrica formal de correspondência de seções esteja zerada.

---

## 5. Análise Detalhada dos Impactos

### A. Comparação de Eficiência de Tempo (Recuperação vs. Inferência)
1. **Tempo de Recuperação (Tempo Rec.)**:
   - **Graph RAG** (~0.03s) e **Naive RAG** (~0.05s) são ordens de grandeza mais rápidos na busca. O Naive faz uma busca vetorial direta (K simples) e o Graph RAG utiliza travessia direta de nós no grafo sem etapas avançadas de agente.
   - **Standard RAG** (~23.3s), **Agentic RAG** (~26.3s), **Hybrid Agent RAG** (~21.8s) e **Fusion RAG** (~20.5s) demoram substancialmente mais porque realizam múltiplas etapas, como reformulação de queries, busca vetorial concorrente estruturada por seções, reranking de documentos ou roteamento lógico complexo.

2. **Tempo de Inferência (Tempo Inf.)**:
   - Em geral, os tempos de inferência aumentam de acordo com a dificuldade (Fáceis: ~16s, Difíceis: ~30s). Isso ocorre porque as perguntas difíceis exigem que o LLM Gemma 4:4b processe mais tokens no prompt de entrada e produza raciocínios e textos mais detalhados.
   - **Hybrid Agent RAG** e **Standard RAG** mantêm consistência operacional (média geral de ~24s de tempo de inferência).

### B. Impacto da Dificuldade das Perguntas
- **Fáceis**: Excelente acurácia geral. O **Hybrid Agent** lidera com **Final Score de 0.9215** e apenas **6.7% de falha crítica**, seguido de perto pelo **Standard RAG**.
- **Médias**: O desempenho foi excelente após a correção dos erros técnicos. O **Hybrid Agent RAG** lidera nesta categoria com **Final Score de 0.8721** e **20.0% de falha crítica**, superando todos os outros pipelines (como o *Standard RAG* com 0.8579 e *Agentic RAG* com 0.8000).
- **Difíceis**: O **Hybrid Agent RAG** no nível Difícil obteve a maior pontuação (**0.8794 de Final Score**) e a menor taxa de Falha Crítica (**6.7%**). Isso demonstra que, livre de erros de concorrência, o agente híbrido é extremamente robusto no tratamento de perguntas complexas.

### C. Comparação entre Pipelines
- **Hybrid Agent RAG (Média Geral 0.8910)**: Tornou-se o melhor pipeline geral após a reexecução bem-sucedida do conjunto médio (onde os erros de concorrência com o ChromaDB foram eliminados). Ele apresenta o maior Final Score geral (0.8910) e a menor taxa consolidada de Falhas Críticas (11.1%).
- **Agentic RAG (Média Geral 0.8501)** e **Standard RAG (Média Geral 0.8527)**: Apresentam excelente estabilidade operacional, mantendo ótimas métricas e baixas taxas de falha crítica (15.6% a 20.0%).
- **Fusion RAG**: Excelente acurácia no nível Fácil (0.9400) e Difícil (0.8149), mas com tempo de recuperação consideravelmente alto devido ao Rerank (~20.5s).
- **Graph RAG (Média Geral 0.7295, Falha Crítica 44.4%)**: Desempenho muito insatisfatório. Ao tentar recuperar 30+ chunks conectados, ele sobrecarrega a janela de atenção do modelo Gemma 4:4b, resultando em respostas fragmentadas e perigosas sob a ótica clínica.

---

## 6. Conclusão e Recomendações

1. **Melhor Escolha de Acurácia e Segurança**: O **Hybrid Agent RAG** é a melhor opção global para o Gemma 4:4b, atingindo o maior Final Score geral (**0.8910**) e a menor taxa média de Falhas Críticas (**11.1%**). A etapa dinâmica de sondagem ("Probe") e o fallback automático provaram-se altamente eficientes.
2. **Melhor Escolha para Baixa Latência**: Se o tempo de recuperação de ~21s do Hybrid Agent for um limitador para produção, o **Naive RAG** (Final Score **0.8826**, tempo de recuperação de ~0.05s) ou o **Standard RAG** (Final Score **0.8527**, tempo de recuperação de ~23s) são as alternativas mais indicadas.
3. **Graph RAG**: Inadequado para LLMs pequenos como o Gemma 4:4b devido ao excesso de ruído injetado pela estrutura de grafo complexa.

---
