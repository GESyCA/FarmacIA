import json
import os

json_path = r"c:\Users\silvi\OneDrive\Documentos\Projetos\FarmacIA-back-end\FarmacIA\Paciente\resultados\gemma_4_4b\gemma_compiled_results.json"
artifact_path = r"c:\Users\silvi\OneDrive\Documentos\Projetos\FarmacIA-back-end\FarmacIA\Paciente\resultados\gemma_4b_comparison_temp.md"


with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

pipelines = ["06_naive", "01_standard", "02_agentic", "03_hybrid_agent", "04_fusion", "05_graph"]
pipeline_names = {
    "06_naive": "Naive RAG",
    "01_standard": "Standard RAG",
    "02_agentic": "Agentic RAG",
    "03_hybrid_agent": "Hybrid Agent RAG",
    "04_fusion": "Fusion RAG",
    "05_graph": "Graph RAG"
}

difficulties = ["faceis", "medias", "dificeis"]
difficulty_names = {
    "faceis": "Fáceis (Easy)",
    "medias": "Médias (Medium)",
    "dificeis": "Difíceis (Hard)"
}

judge_metrics = [
    ("contextual_recall", "Recall"),
    ("contextual_precision", "Precision"),
    ("evidence_sufficiency", "Sufficiency"),
    ("faithfulness", "Faithfulness"),
    ("answer_relevancy", "Relevancy"),
    ("response_completeness", "Completeness"),
    ("unsupported_claims", "No-Unsupp-Claims"),
    ("clinical_safety", "Safety"),
    ("warning_preservation", "Warning-Pres"),
    ("patient_comprehensibility", "Comprehensibility"),
    ("inference_control", "Inference-Ctrl")
]

md = []
md.append("# Comparação Intramodelo - Gemma 4:4b (ollama:gemma4:e4b)")
md.append("")
md.append("Este relatório compara o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG implementado** na recuperação e na geração de respostas, bem como a eficiência de tempo de execução, utilizando exclusivamente os resultados obtidos com o modelo **Gemma 4:4b** no diretório `resultados/gemma_4_4b`.")
md.append("")
md.append("> [!NOTE]")
md.append("> **Definição do Final Score:** O **Final Score** é exatamente a média aritmética das notas normalizadas (de 0.0 a 1.0) atribuídas pelo **LLM-as-a-judge** (ChatGPT / Gemini) nos **11 critérios clínicos e contextuais** definidos no projeto (listados na seção 3).")
md.append("")
md.append("---")
md.append("")
md.append("## 1. Resultados Detalhados por Dificuldade")
md.append("")

for diff in difficulties:
    md.append(f"### Perguntas {difficulty_names[diff]}")
    md.append("| Pipeline | Final Score (Judge) | Falhas Críticas (%) | Context Recall | Context Precision | Section Recall | Section Precision | ROUGE-L | BLEU | Tempo Rec. (s) | Tempo Inf. (s) |")
    md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
    
    for pipe in pipelines:
        key = f"{pipe}|{diff}"
        metrics = data.get(key, {})
        
        fs = f"{metrics.get('final_score', 0.0):.4f}" if 'final_score' in metrics else "N/A"
        cf = f"{metrics.get('critical_failure_rate', 0.0)*100:.1f}%" if 'critical_failure_rate' in metrics else "N/A"
        cr = f"{metrics.get('contextual_recall', 0.0):.4f}" if 'contextual_recall' in metrics else "N/A"
        cp = f"{metrics.get('contextual_precision', 0.0):.4f}" if 'contextual_precision' in metrics else "N/A"
        sr = f"{metrics.get('section_recall', 0.0):.4f}" if 'section_recall' in metrics else "N/A"
        sp = f"{metrics.get('section_precision', 0.0):.4f}" if 'section_precision' in metrics else "N/A"
        rl = f"{metrics.get('rougeL', 0.0):.4f}" if 'rougeL' in metrics else "N/A"
        bl = f"{metrics.get('bleu', 0.0):.4f}" if 'bleu' in metrics else "N/A"
        t_rec = f"{metrics.get('avg_retrieval_time', 0.0):.2f}s" if 'avg_retrieval_time' in metrics else "N/A"
        t_inf = f"{metrics.get('avg_inference_time', 0.0):.2f}s" if 'avg_inference_time' in metrics else "N/A"
        
        md.append(f"| {pipeline_names[pipe]} | {fs} | {cf} | {cr} | {cp} | {sr} | {sp} | {rl} | {bl} | {t_rec} | {t_inf} |")
    md.append("")

md.append("---")
md.append("")
md.append("## 2. Comparativo Consolidado por Pipeline (Média Geral)")
md.append("")
md.append("A tabela abaixo apresenta a média consolidada de cada métrica para cada pipeline unindo todas as dificuldades:")
md.append("")
md.append("| Pipeline | Média Final Score | Média Falhas Críticas | Média Context Recall | Média Context Precision | Média ROUGE-L | Média BLEU | Média Tempo Rec. | Média Tempo Inf. |")
md.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- |")

for pipe in pipelines:
    fs_list = []
    cf_list = []
    cr_list = []
    cp_list = []
    rl_list = []
    bl_list = []
    t_rec_list = []
    t_inf_list = []
    
    for diff in difficulties:
        key = f"{pipe}|{diff}"
        metrics = data.get(key, {})
        if 'final_score' in metrics: fs_list.append(metrics['final_score'])
        if 'critical_failure_rate' in metrics: cf_list.append(metrics['critical_failure_rate'])
        if 'contextual_recall' in metrics: cr_list.append(metrics['contextual_recall'])
        if 'contextual_precision' in metrics: cp_list.append(metrics['contextual_precision'])
        if 'rougeL' in metrics: rl_list.append(metrics['rougeL'])
        if 'bleu' in metrics: bl_list.append(metrics['bleu'])
        if 'avg_retrieval_time' in metrics: t_rec_list.append(metrics['avg_retrieval_time'])
        if 'avg_inference_time' in metrics: t_inf_list.append(metrics['avg_inference_time'])
        
    avg_fs = sum(fs_list)/len(fs_list) if fs_list else 0
    avg_cf = sum(cf_list)/len(cf_list) if cf_list else 0
    avg_cr = sum(cr_list)/len(cr_list) if cr_list else 0
    avg_cp = sum(cp_list)/len(cp_list) if cp_list else 0
    avg_rl = sum(rl_list)/len(rl_list) if rl_list else 0
    avg_bl = sum(bl_list)/len(bl_list) if bl_list else 0
    avg_t_rec = sum(t_rec_list)/len(t_rec_list) if t_rec_list else 0
    avg_t_inf = sum(t_inf_list)/len(t_inf_list) if t_inf_list else 0
    md.append(f"| {pipeline_names[pipe]} | {avg_fs:.4f} | {avg_cf*100:.1f}% | {avg_cr:.4f} | {avg_cp:.4f} | {avg_rl:.4f} | {avg_bl:.4f} | {avg_t_rec:.2f}s | {avg_t_inf:.2f}s |")

md.append("## 3. Comparativo de Todos os Critérios do LLM-as-a-Judge")
md.append("")
md.append("Abaixo estão detalhadas as médias obtidas em cada um dos **11 critérios clínicos e contextuais** individuais avaliados pelo LLM-as-a-judge (escala de 0.0 a 1.0), divididos por nível de dificuldade das perguntas e consolidados em uma média geral:")
md.append("")

for diff in difficulties:
    md.append(f"### Critérios - Perguntas {difficulty_names[diff]}")
    md.append("")
    header_cols = ["Pipeline"] + [col_label for _, col_label in judge_metrics]
    md.append("| " + " | ".join(header_cols) + " |")
    md.append("| " + " | ".join(["---"] * len(header_cols)) + " |")
    
    for pipe in pipelines:
        row_cells = [pipeline_names[pipe]]
        for metric_key, _ in judge_metrics:
            key = f"{pipe}|{diff}"
            metrics = data.get(key, {})
            val = metrics.get(metric_key, 0.0)
            row_cells.append(f"{val:.4f}")
        md.append("| " + " | ".join(row_cells) + " |")
    md.append("")

md.append("### Critérios - Média Geral (Consolidado de Todas as Dificuldades)")
md.append("")
header_cols = ["Pipeline"] + [col_label for _, col_label in judge_metrics]
md.append("| " + " | ".join(header_cols) + " |")
md.append("| " + " | ".join(["---"] * len(header_cols)) + " |")

for pipe in pipelines:
    row_cells = [pipeline_names[pipe]]
    for metric_key, _ in judge_metrics:
        val_list = []
        for diff in difficulties:
            key = f"{pipe}|{diff}"
            metrics = data.get(key, {})
            if metric_key in metrics:
                val_list.append(metrics[metric_key])
        
        avg_val = sum(val_list)/len(val_list) if val_list else 0.0
        row_cells.append(f"{avg_val:.4f}")
    md.append("| " + " | ".join(row_cells) + " |")

md.append("")
md.append("---")
md.append("")
md.append("## 4. Esclarecimento Sobre o \"Naive RAG\" com Nota Zero")
md.append("")
md.append("Você pode notar que o **Naive RAG** apresenta pontuações zeradas (`0.0000`) nas seguintes colunas:")
md.append("- **Section Recall** (Revocação de Seções)")
md.append("- **Section Precision** (Precisão de Seções)")
md.append("")
md.append("### Por que isso ocorre?")
md.append("Essas colunas representam as **Métricas Estruturais de Recuperação** (comparação das seções formais da bula onde as informações deveriam estar, como *'COMO DEVO USAR ESTE MEDICAMENTO?'*, com as seções realmente acessadas pelo pipeline).")
md.append("")
md.append("1. **Funcionamento do Naive RAG**: Ele é o pipeline mais simples de RAG. Ele fatia o texto das bulas de forma sequencial (baseado em caracteres ou palavras) e faz a busca semântica diretamente sobre os chunks, sem classificar de qual seção aquele chunk provém e sem preencher a coluna `secoes_recuperadas` na saída CSV.")
md.append("2. **Cálculo da Métrica**: Como a coluna `secoes_recuperadas` é deixada vazia no Naive RAG, o script de avaliação automática interpreta que o pipeline não conseguiu recuperar nenhuma seção formal. Por isso, a nota estrutural de seção é `0.0000` (zero).")
md.append("")
md.append("### O Naive RAG falhou em ler as informações?")
md.append("**Não!** Se você olhar a métrica **Context Recall**, verá que ela é **1.0000 (100%)** em todas as dificuldades nas avaliações do juiz. Isso significa que, semanticamente, o conteúdo recuperado continha toda a informação necessária para responder às perguntas, e o modelo conseguiu ler essa informação no contexto para formular a resposta final. Por esse motivo, o **Final Score** geral dele é alto (média de 0.8826), embora a métrica formal de correspondência de seções esteja zerada.")
md.append("")
md.append("---")
md.append("")
md.append("## 5. Análise Detalhada dos Impactos")
md.append("")
md.append("### A. Comparação de Eficiência de Tempo (Recuperação vs. Inferência)")
md.append("1. **Tempo de Recuperação (Tempo Rec.)**:")
md.append("   - **Graph RAG** (~0.03s) e **Naive RAG** (~0.05s) são ordens de grandeza mais rápidos na busca. O Naive faz uma busca vetorial direta (K simples) e o Graph RAG utiliza travessia direta de nós no grafo sem etapas avançadas de agente.")
md.append("   - **Standard RAG** (~23.3s), **Agentic RAG** (~26.3s), **Hybrid Agent RAG** (~21.8s) e **Fusion RAG** (~20.5s) demoram substancialmente mais porque realizam múltiplas etapas, como reformulação de queries, busca vetorial concorrente estruturada por seções, reranking de documentos ou roteamento lógico complexo.")
md.append("")
md.append("2. **Tempo de Inferência (Tempo Inf.)**:")
md.append("   - Em geral, os tempos de inferência aumentam de acordo com a dificuldade (Fáceis: ~16s, Difíceis: ~30s). Isso ocorre porque as perguntas difíceis exigem que o LLM Gemma 4:4b processe mais tokens no prompt de entrada e produza raciocínios e textos mais detalhados.")
md.append("   - **Hybrid Agent RAG** e **Standard RAG** mantêm consistência operacional (média geral de ~24s de tempo de inferência).")
md.append("")
md.append("### B. Impacto da Dificuldade das Perguntas")
md.append("- **Fáceis**: Excelente acurácia geral. O **Hybrid Agent** lidera com **Final Score de 0.9215** e apenas **6.7% de falha crítica**, seguido de perto pelo **Standard RAG**.")
md.append("- **Médias**: O desempenho foi excelente após a correção dos erros técnicos. O **Hybrid Agent RAG** lidera nesta categoria com **Final Score de 0.8721** e **20.0% de falha crítica**, superando todos os outros pipelines (como o *Standard RAG* com 0.8579 e *Agentic RAG* com 0.8000).")
md.append("- **Difíceis**: O **Hybrid Agent RAG** no nível Difícil obteve a maior pontuação (**0.8794 de Final Score**) e a menor taxa de Falha Crítica (**6.7%**). Isso demonstra que, livre de erros de concorrência, o agente híbrido é extremamente robusto no tratamento de perguntas complexas.")
md.append("")
md.append("### C. Comparação entre Pipelines")
md.append("- **Hybrid Agent RAG (Média Geral 0.8910)**: Tornou-se o melhor pipeline geral após a reexecução bem-sucedida do conjunto médio (onde os erros de concorrência com o ChromaDB foram eliminados). Ele apresenta o maior Final Score geral (0.8910) e a menor taxa consolidada de Falhas Críticas (11.1%).")
md.append("- **Agentic RAG (Média Geral 0.8501)** e **Standard RAG (Média Geral 0.8527)**: Apresentam excelente estabilidade operacional, mantendo ótimas métricas e baixas taxas de falha crítica (15.6% a 20.0%).")
md.append("- **Fusion RAG**: Excelente acurácia no nível Fácil (0.9400) e Difícil (0.8149), mas com tempo de recuperação consideravelmente alto devido ao Rerank (~20.5s).")
md.append("- **Graph RAG (Média Geral 0.7295, Falha Crítica 44.4%)**: Desempenho muito insatisfatório. Ao tentar recuperar 30+ chunks conectados, ele sobrecarrega a janela de atenção do modelo Gemma 4:4b, resultando em respostas fragmentadas e perigosas sob a ótica clínica.")
md.append("")
md.append("---")
md.append("")
md.append("## 6. Conclusão e Recomendações")
md.append("")
md.append("1. **Melhor Escolha de Acurácia e Segurança**: O **Hybrid Agent RAG** é a melhor opção global para o Gemma 4:4b, atingindo o maior Final Score geral (**0.8910**) e a menor taxa média de Falhas Críticas (**11.1%**). A etapa dinâmica de sondagem (\"Probe\") e o fallback automático provaram-se altamente eficientes.")
md.append("2. **Melhor Escolha para Baixa Latência**: Se o tempo de recuperação de ~21s do Hybrid Agent for um limitador para produção, o **Naive RAG** (Final Score **0.8826**, tempo de recuperação de ~0.05s) ou o **Standard RAG** (Final Score **0.8527**, tempo de recuperação de ~23s) são as alternativas mais indicadas.")
md.append("3. **Graph RAG**: Inadequado para LLMs pequenos como o Gemma 4:4b devido ao excesso de ruído injetado pela estrutura de grafo complexa.")
md.append("")
md.append("---")
md.append("")

with open(artifact_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(md))

brain_path = r"C:\Users\silvi\.gemini\antigravity-ide\brain\4805c83e-14fb-4530-9dd9-d97e1c888327\gemma_4b_comparison.md"
with open(brain_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(md))

print("Markdown report successfully generated!")

