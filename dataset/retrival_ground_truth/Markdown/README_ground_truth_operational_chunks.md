# Ground Truth de Recuperação — chunks operacionais

## Arquivos de entrada usados

- `chunks.jsonl` — inventário operacional de chunks usado como única fonte de IDs gold.
- `faceis_revisadas.csv` — perguntas/respostas fáceis, preservadas como entrada fixa.
- `medias_revisadas.csv` — perguntas/respostas médias, preservadas como entrada fixa.
- `dificeis_revisadas.csv` — perguntas/respostas difíceis, preservadas como entrada fixa.

O dataset de perguntas e respostas foi preservado. Este GT não cria novas perguntas e não altera respostas esperadas; ele apenas adiciona evidências gold de recuperação alinhadas aos chunks operacionais.

## Arquivos gerados

- `ground_truth_retrieval_operational_chunks.jsonl`: um registro por pergunta, com metadados originais, evidências gold e regra operacional de sucesso.
- `ground_truth_operational_chunks_flat.csv`: uma linha por evidência/chunk gold.
- `ground_truth_operational_chunks_summary.csv`: uma linha por pergunta.
- `operational_chunks_inventory.csv`: inventário dos chunks carregados de `chunks.jsonl`.
- `human_review_items.csv`: itens não totalmente alinhados automaticamente.

## Como usar nas métricas

### Recall@K binário

Use `primary_gold_chunk_id` ou `essential_gold_chunk_ids`. A recuperação é sucesso se ao menos um chunk essencial da pergunta aparecer entre os top K recuperados.

### Evidence Set Recall@K

Para cada pergunta, calcule a fração dos `essential_gold_chunk_ids` presentes no top K. Quando houver múltiplas evidências essenciais, essa métrica mede cobertura do conjunto necessário.

### MRR@K

Use o rank do primeiro chunk recuperado que pertença aos `essential_gold_chunk_ids`. O ganho é `1/rank` se o primeiro essencial estiver no top K; caso contrário, 0.

### nDCG@K

Use `relevance_grade` como ganho por chunk: 3 para evidência essencial e diretamente suficiente, 2 para evidência complementar ou parcialmente suficiente, 1 para evidência marginal. Calcule o DCG dos chunks recuperados que aparecem em `all_relevant_gold_chunk_ids` e normalize pelo IDCG da pergunta.

### Context Precision

Compare os chunks no contexto recuperado com `all_relevant_gold_chunk_ids`. Chunks gold devem contar como relevantes; chunks fora desse conjunto devem ser tratados como não gold para esta avaliação, salvo revisão humana posterior.

## Interpretação dos campos

- `evidence_type = essential`: chunk necessário ou central para responder corretamente.
- `evidence_type = supporting`: chunk útil para contexto, confirmação ou completude, mas não central sozinho.
- `relevance_grade = 3`: evidência essencial diretamente suficiente.
- `relevance_grade = 2`: evidência relevante complementar ou parcialmente suficiente.
- `relevance_grade = 1`: evidência marginalmente útil.
- `match_confidence = high`: o chunk sustenta claramente a resposta.
- `match_confidence = medium`: o chunk sustenta parcialmente ou exige interpretação.
- `match_confidence = low`: relação fraca, ambígua ou dependente de revisão.

## Tratamento de status

- `matched`: há evidência essencial suficiente nos chunks operacionais.
- `partial_match`: há evidência relevante, mas nem todas as seções/evidências esperadas foram cobertas.
- `needs_review`: há evidência candidata, mas a confiança ou alinhamento exige auditoria humana.
- `no_gold_chunk_found`: nenhum chunk operacional sustenta adequadamente a resposta; não foi inventada evidência.

## Validações realizadas

- `chunks.jsonl` foi lido e validado como JSONL. Erros encontrados: 0.
- Total de perguntas lidas: 45.
- Total de registros no GT: 45.
- Todos os `gold_chunk_id` usados existem em `chunks.jsonl`.
- Nenhuma pergunta nova foi criada; IDs estáveis `q001`, `q002`, ... foram atribuídos porque os CSVs de entrada não tinham `question_id`.

## Resumo

- Perguntas originais: 45
- Perguntas no GT: 45
- Chunks operacionais: 115
- Status `matched`: 33
- Status `partial_match`: 12
- Status `needs_review`: 0
- Status `no_gold_chunk_found`: 0
- Evidências gold totais: 185
- Evidências essential: 98
- Evidências supporting: 87
- Distribuição de confiança: {'high': 173, 'medium': 9, 'low': 3}
- Itens para revisão humana: ['q010', 'q021', 'q022', 'q024', 'q025', 'q026', 'q036', 'q037', 'q038', 'q039', 'q040', 'q043']
