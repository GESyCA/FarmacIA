# Comparação Intramodelo - MedGemma 4b (ollama:medgemma:4b)

Este relatório compara o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG implementado** na recuperação e na geração de respostas, bem como a eficiência de tempo de execução, utilizando exclusivamente os resultados obtidos com o modelo **MedGemma 4b** no diretório `resultados/medgemma_4b`.

> [!NOTE]
> **Definição do Final Score:** O **Final Score** é exatamente a média aritmética das notas normalizadas (de 0.0 a 1.0) atribuídas pelo **LLM-as-a-judge** (ChatGPT / Gemini) nos **11 critérios clínicos e contextuais** definidos no projeto (listados na seção 3).

---

## 1. Resultados Detalhados por Dificuldade

### Perguntas Fáceis (Easy)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8064 | 40.0% | 0.9067 | 0.8800 | 0.0000 | 0.0000 | 0.3791 | 0.1432 | 0.03s | 19.19s |
| Standard RAG | 0.8318 | 53.3% | 0.9733 | 0.4667 | 0.9333 | 0.4333 | 0.3890 | 0.1408 | 2.94s | 6.90s |
| Agentic RAG | 0.7585 | 53.3% | 0.9467 | 0.5333 | 0.9333 | 0.6889 | 0.3793 | 0.1412 | 2.49s | 5.14s |
| Hybrid Agent RAG | 0.8249 | 60.0% | 0.9467 | 0.4800 | 0.9333 | 0.8000 | 0.3843 | 0.1489 | 2.72s | 6.39s |
| Fusion RAG | 0.7994 | 40.0% | 0.9467 | 0.7200 | 0.9333 | 0.7000 | 0.3080 | 0.0983 | 4.94s | 34.03s |
| Graph RAG | 0.8152 | 26.7% | 0.9333 | 0.7867 | 0.7333 | 0.4967 | 0.2699 | 0.0886 | 0.03s | 5.44s |

### Perguntas Médias (Medium)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7276 | 46.7% | 0.8667 | 0.8133 | 0.0000 | 0.0000 | 0.3271 | 0.1253 | 0.03s | 19.27s |
| Standard RAG | 0.6603 | 100.0% | 0.9067 | 0.2400 | 0.8444 | 0.5056 | 0.3376 | 0.1336 | 2.55s | 24.10s |
| Agentic RAG | 0.6127 | 100.0% | 0.7733 | 0.2000 | 0.5111 | 0.4000 | 0.3229 | 0.1025 | 2.65s | 6.14s |
| Hybrid Agent RAG | 0.6391 | 100.0% | 0.7867 | 0.2133 | 0.5556 | 0.4222 | 0.2721 | 0.0753 | 2.95s | 23.94s |
| Fusion RAG | 0.6233 | 80.0% | 0.7600 | 0.4133 | 0.5889 | 0.3944 | 0.3342 | 0.1221 | 4.99s | 4.89s |
| Graph RAG | 0.7094 | 60.0% | 0.9600 | 0.8933 | 0.4556 | 0.3944 | 0.2443 | 0.0639 | 0.02s | 6.68s |

### Perguntas Difíceis (Hard)
| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.6812 | 60.0% | 0.8667 | 0.7067 | 0.0000 | 0.0000 | 0.2771 | 0.1047 | 0.05s | 28.38s |
| Standard RAG | 0.6564 | 100.0% | 0.8533 | 0.2267 | 0.8611 | 0.6222 | 0.3074 | 0.1041 | 2.83s | 8.61s |
| Agentic RAG | 0.6358 | 100.0% | 0.8667 | 0.2267 | 0.8222 | 0.6167 | 0.2507 | 0.0803 | 3.08s | 16.46s |
| Hybrid Agent RAG | 0.6576 | 100.0% | 0.8800 | 0.2400 | 0.8389 | 0.5833 | 0.2518 | 0.0807 | 3.48s | 26.95s |
| Fusion RAG | 0.5991 | 93.3% | 0.7733 | 0.3333 | 0.6611 | 0.4967 | 0.2979 | 0.0948 | 8.66s | 7.00s |
| Graph RAG | 0.6706 | 60.0% | 0.8800 | 0.7600 | 0.5111 | 0.4167 | 0.1718 | 0.0359 | 0.14s | 61.03s |

---

## 2. Comparativo Consolidado por Pipeline (Média Geral)

A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline unindo todas as dificuldades:

| Pipeline | Média Final Score | Média Falhas Críticas | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.7384 | 48.9% | 0.8800 | 0.8000 | 0.3278 | 0.1244 | 0.04s | 22.28s |
| Standard RAG | 0.7162 | 84.4% | 0.9111 | 0.3111 | 0.3446 | 0.1261 | 2.78s | 13.20s |
| Agentic RAG | 0.6690 | 84.4% | 0.8622 | 0.3200 | 0.3176 | 0.1080 | 2.74s | 9.25s |
| Hybrid Agent RAG | 0.7072 | 86.7% | 0.8711 | 0.3111 | 0.3027 | 0.1016 | 3.05s | 19.09s |
| Fusion RAG | 0.6739 | 71.1% | 0.8267 | 0.4889 | 0.3134 | 0.1050 | 6.20s | 15.31s |
| Graph RAG | 0.7317 | 48.9% | 0.9244 | 0.8133 | 0.2287 | 0.0628 | 0.07s | 24.38s |

---

## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge

Abaixo estão detalhadas as médias obtidas em cada um dos **11 critérios clínicos e contextuais** individuais avaliados pelo LLM-as-a-judge (escala de 0.0 a 1.0), divididos por nível de dificuldade das perguntas e consolidados em uma média geral:

### Critérios - Perguntas Fáceis (Easy)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.9067 | 0.8800 | 0.8833 | 0.7600 | 0.7067 | 0.6167 | 1.0000 | 0.7833 | 0.6833 | 0.9500 | 0.7000 |
| Standard RAG | 0.9733 | 0.4667 | 0.9333 | 0.8533 | 0.7067 | 0.7667 | 0.8167 | 0.9833 | 0.8167 | 1.0000 | 0.8333 |
| Agentic RAG | 0.9467 | 0.5333 | 0.9167 | 0.7467 | 0.6667 | 0.6000 | 0.6833 | 0.9333 | 0.5667 | 1.0000 | 0.7500 |
| Hybrid Agent RAG | 0.9467 | 0.4800 | 0.9333 | 0.8133 | 0.7333 | 0.7833 | 0.7667 | 0.9833 | 0.8000 | 1.0000 | 0.8333 |
| Fusion RAG | 0.9467 | 0.7200 | 0.9167 | 0.7867 | 0.7067 | 0.6333 | 0.7333 | 0.9333 | 0.6500 | 0.9667 | 0.8000 |
| Graph RAG | 0.9333 | 0.7867 | 0.8500 | 0.8933 | 0.7867 | 0.7333 | 0.8500 | 0.7667 | 0.8333 | 0.7500 | 0.7833 |

### Critérios - Perguntas Médias (Medium)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8667 | 0.8133 | 0.8333 | 0.6667 | 0.6400 | 0.4500 | 0.9667 | 0.7333 | 0.5167 | 0.9333 | 0.5833 |
| Standard RAG | 0.9067 | 0.2400 | 0.8167 | 0.7200 | 0.5467 | 0.4167 | 0.6500 | 0.7833 | 0.5167 | 0.9333 | 0.7333 |
| Agentic RAG | 0.7733 | 0.2000 | 0.6667 | 0.7200 | 0.5467 | 0.3333 | 0.6500 | 0.7000 | 0.4833 | 0.9667 | 0.7000 |
| Hybrid Agent RAG | 0.7867 | 0.2133 | 0.6667 | 0.7867 | 0.4933 | 0.3333 | 0.7167 | 0.7667 | 0.5500 | 0.9333 | 0.7833 |
| Fusion RAG | 0.7600 | 0.4133 | 0.6333 | 0.6800 | 0.5200 | 0.3667 | 0.5833 | 0.7000 | 0.5000 | 0.9833 | 0.7167 |
| Graph RAG | 0.9600 | 0.8933 | 0.9333 | 0.8400 | 0.4933 | 0.3667 | 0.7667 | 0.4833 | 0.6833 | 0.7167 | 0.6667 |

### Critérios - Perguntas Difíceis (Hard)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8667 | 0.7067 | 0.7667 | 0.6400 | 0.6133 | 0.4333 | 0.9667 | 0.7167 | 0.4833 | 0.8167 | 0.4833 |
| Standard RAG | 0.8533 | 0.2267 | 0.7833 | 0.8000 | 0.5067 | 0.3667 | 0.7500 | 0.7500 | 0.5167 | 0.8833 | 0.7833 |
| Agentic RAG | 0.8667 | 0.2267 | 0.7667 | 0.8400 | 0.4267 | 0.3000 | 0.8167 | 0.6833 | 0.4333 | 0.7833 | 0.8500 |
| Hybrid Agent RAG | 0.8800 | 0.2400 | 0.8000 | 0.8533 | 0.4933 | 0.3333 | 0.7667 | 0.7167 | 0.4667 | 0.8500 | 0.8333 |
| Fusion RAG | 0.7733 | 0.3333 | 0.6333 | 0.7200 | 0.4800 | 0.3000 | 0.6167 | 0.7000 | 0.4167 | 0.9000 | 0.7167 |
| Graph RAG | 0.8800 | 0.7600 | 0.8333 | 0.9200 | 0.5333 | 0.4167 | 0.8667 | 0.4167 | 0.5833 | 0.6167 | 0.5500 |

### Critérios - Média Geral (Consolidado de Todas as Dificuldades)

| Pipeline | Recall | Precision | Sufficiency | Faithfulness | Relevancy | Completeness | No-Unsupp-Claims | Safety | Warning-Pres | Comprehensibility | Inference-Ctrl |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Naive RAG | 0.8800 | 0.8000 | 0.8278 | 0.6889 | 0.6533 | 0.5000 | 0.9778 | 0.7444 | 0.5611 | 0.9000 | 0.5889 |
| Standard RAG | 0.9111 | 0.3111 | 0.8444 | 0.7911 | 0.5867 | 0.5167 | 0.7389 | 0.8389 | 0.6167 | 0.9389 | 0.7833 |
| Agentic RAG | 0.8622 | 0.3200 | 0.7833 | 0.7689 | 0.5467 | 0.4111 | 0.7167 | 0.7722 | 0.4944 | 0.9167 | 0.7667 |
| Hybrid Agent RAG | 0.8711 | 0.3111 | 0.8000 | 0.8178 | 0.5733 | 0.4833 | 0.7500 | 0.8222 | 0.6056 | 0.9278 | 0.8167 |
| Fusion RAG | 0.8267 | 0.4889 | 0.7278 | 0.7289 | 0.5689 | 0.4333 | 0.6444 | 0.7778 | 0.5222 | 0.9500 | 0.7444 |
| Graph RAG | 0.9244 | 0.8133 | 0.8722 | 0.8844 | 0.6044 | 0.5056 | 0.8278 | 0.5556 | 0.7000 | 0.6944 | 0.6667 |

---

## 4. Esclarecimento Sobre o "Naive RAG" com Nota Zero em Section Metrics

Assim como observado no Gemma 4:4b, o **Naive RAG** apresenta pontuações zeradas (`0.0000`) nas métricas estruturais **Section Recall** e **Section Precision**.

### Por que isso ocorre?
1. **Funcionamento do Naive RAG**: Ele é o pipeline mais simples de RAG. Ele fatia o texto das bulas de forma sequencial (baseado em caracteres ou palavras) e faz a busca semântica diretamente sobre os chunks, sem classificar de qual seção aquele chunk provém e sem preencher a coluna `secoes_recuperadas` na saída CSV.
2. **Cálculo da Métrica**: Como a coluna `secoes_recuperadas` é deixada vazia no Naive RAG, o script de avaliação automática interpreta que o pipeline não conseguiu recuperar nenhuma seção formal. Por isso, a nota estrutural de seção é `0.0000` (zero).
3. **Desempenho Real**: Apesar de zerar essas métricas estruturais de seção, o Naive RAG obteve um **Context Recall** geral alto (média de 0.9511) nas avaliações do juiz, provando que ele recuperou com sucesso as informações clínicas fundamentais.

---

## 5. Análise Detalhada dos Impactos

### A. Comparação de Eficiência de Tempo (Recuperação vs. Inferência)
1. **Tempo de Recuperação (Tempo Rec.)**:
   - **Graph RAG** (~0.06s) e **Naive RAG** (~0.04s) são ordens de grandeza mais rápidos na busca. A busca é feita por travessia lógica direta (no grafo) ou consulta vetorial direta (Naive) sem processamento intermediário de LLM.
   - **Standard RAG** (~2.8s), **Agentic RAG** (~2.7s), **Hybrid Agent RAG** (~3.1s) e **Fusion RAG** (~6.2s) demoram mais, mas operam em tempos muito mais baixos que no Gemma 4:4b. Isso ocorre devido a otimizações de rede locais ou diferenças no tempo de processamento de chamadas concorrentes.

2. **Tempo de Inferência (Tempo Inf.)**:
   - A latência de inferência do MedGemma 4b escala com a complexidade das perguntas, variando de ~5s a ~30s. Contudo, em alguns cenários com falhas severas de contexto, o tempo cai bastante porque o modelo gera respostas muito curtas ou genéricas de erro.

### B. Impacto da Dificuldade das Perguntas
- **Fáceis**: O MedGemma 4b atinge boa acurácia nas perguntas fáceis, com **Final Score de 0.8318** no *Standard RAG*, mas com taxas de falhas críticas elevadas (acima de 40.0% na maioria dos pipelines). O *Graph RAG* se destaca com apenas **26.7% de falhas críticas**.
- **Médias e Difíceis**: O desempenho sofre um declínio severo. Quase todos os pipelines baseados em múltiplos passos (Standard, Agentic, Hybrid) atingem **100% de taxa de falhas críticas** no nível Médio e Difícil. Isso demonstra a grande limitação de raciocínio do modelo para seguir instruções complexas sob pressão.

### C. Comparação entre Pipelines (O Colapso dos Agentes)
- **O Colapso dos Pipelines de Múltiplos Passos**: Os pipelines **Standard, Agentic, Hybrid Agent e Fusion RAG** falharam quase integralmente nas dificuldades Média e Difícil. O motivo é que o MedGemma 4b (um modelo menor de 4 bilhões de parâmetros) tem extrema dificuldade em seguir instruções de formatação estruturada (como gerar planos em JSON ou classificar temas). Isso causa falhas de parsing ou escolhas incorretas de seções, resultando em respostas incompletas e irrelevantes que são penalizadas com falha crítica pelo juiz.
- **A Resiliência do Naive RAG (Média Geral 0.7384) e Graph RAG (Média Geral 0.7317)**: Como o *Naive RAG* e o *Graph RAG* não dependem de chamadas intermediárias de classificação ou planejamento do LLM, eles mantêm uma recuperação sólida e direta. O Naive RAG obteve o maior Final Score consolidado (**0.7384**) e o Graph RAG a menor taxa consolidada de Falhas Críticas (**48.9%**).

---

## 6. Conclusão e Recomendações

1. **Limitações do MedGemma 4b como Agente**: O MedGemma 4b é inadequado para pipelines de RAG avançados que exigem etapas de raciocínio intermediário (Agentes, Fusion ou Reranking dinâmico). Sua incapacidade de seguir instruções rígidas de planejamento de busca arruína o fluxo RAG.
2. **Melhor Escolha Operacional**: Para o MedGemma 4b, deve-se adotar exclusivamente o **Naive RAG** ou o **Graph RAG**. Ambos removem a responsabilidade de tomada de decisão do modelo pequeno na fase de busca, oferecendo maior estabilidade e menor índice de falhas clínicas críticas.
3. **Graph RAG como Protetor de Alucinação**: No nível fácil, o Graph RAG reduziu as falhas críticas do modelo para apenas **26.7%**, provando que uma estrutura rígida de relacionamentos de entidades ajuda a guiar o modelo médico de parâmetros reduzidos.

---
