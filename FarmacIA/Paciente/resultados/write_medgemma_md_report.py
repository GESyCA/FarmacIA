import json
import os

json_path = r"c:\Users\silvi\OneDrive\Documentos\Projetos\FarmacIA-back-end\FarmacIA\Paciente\resultados\medgemma_4b\medgemma_compiled_results.json"
local_artifact_path = r"c:\Users\silvi\OneDrive\Documentos\Projetos\FarmacIA-back-end\FarmacIA\Paciente\resultados\medgemma_4b_comparison.md"
brain_artifact_path = r"C:\Users\silvi\.gemini\antigravity-ide\brain\4805c83e-14fb-4530-9dd9-d97e1c888327\medgemma_4b_comparison.md"

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
md.append("# Comparação Intramodelo - MedGemma 4b (ollama:medgemma:4b)")
md.append("")
md.append("Este relatório compara o impacto do **nível de dificuldade das perguntas** e do **pipeline de RAG implementado** na recuperação e na geração de respostas, bem como a eficiência de tempo de execução, utilizando exclusivamente os resultados obtidos com o modelo **MedGemma 4b** no diretório `resultados/medgemma_4b`.")
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

md.append("")
md.append("---")
md.append("")
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
md.append("## 4. Esclarecimento Sobre o \"Naive RAG\" com Nota Zero em Section Metrics")
md.append("")
md.append("Assim como observado no Gemma 4:4b, o **Naive RAG** apresenta pontuações zeradas (`0.0000`) nas métricas estruturais **Section Recall** e **Section Precision**.")
md.append("")
md.append("### Por que isso ocorre?")
md.append("1. **Funcionamento do Naive RAG**: Ele é o pipeline mais simples de RAG. Ele fatia o texto das bulas de forma sequencial (baseado em caracteres ou palavras) e faz a busca semântica diretamente sobre os chunks, sem classificar de qual seção aquele chunk provém e sem preencher a coluna `secoes_recuperadas` na saída CSV.")
md.append("2. **Cálculo da Métrica**: Como a coluna `secoes_recuperadas` é deixada vazia no Naive RAG, o script de avaliação automática interpreta que o pipeline não conseguiu recuperar nenhuma seção formal. Por isso, a nota estrutural de seção é `0.0000` (zero).")
md.append("3. **Desempenho Real**: Apesar de zerar essas métricas estruturais de seção, o Naive RAG obteve um **Context Recall** geral alto (média de 0.9511) nas avaliações do juiz, provando que ele recuperou com sucesso as informações clínicas fundamentais.")
md.append("")
md.append("---")
md.append("")
md.append("## 5. Análise Detalhada dos Impactos")
md.append("")
md.append("### A. Comparação de Eficiência de Tempo (Recuperação vs. Inferência)")
md.append("1. **Tempo de Recuperação (Tempo Rec.)**:")
md.append("   - **Graph RAG** (~0.06s) e **Naive RAG** (~0.04s) são ordens de grandeza mais rápidos na busca. A busca é feita por travessia lógica direta (no grafo) ou consulta vetorial direta (Naive) sem processamento intermediário de LLM.")
md.append("   - **Standard RAG** (~2.8s), **Agentic RAG** (~2.7s), **Hybrid Agent RAG** (~3.1s) e **Fusion RAG** (~6.2s) demoram mais, mas operam em tempos muito mais baixos que no Gemma 4:4b. Isso ocorre devido a otimizações de rede locais ou diferenças no tempo de processamento de chamadas concorrentes.")
md.append("")
md.append("2. **Tempo de Inferência (Tempo Inf.)**:")
md.append("   - A latência de inferência do MedGemma 4b escala com a complexidade das perguntas, variando de ~5s a ~30s. Contudo, em alguns cenários com falhas severas de contexto, o tempo cai bastante porque o modelo gera respostas muito curtas ou genéricas de erro.")
md.append("")
md.append("### B. Impacto da Dificuldade das Perguntas")
md.append("- **Fáceis**: O MedGemma 4b atinge boa acurácia nas perguntas fáceis, com **Final Score de 0.8318** no *Standard RAG*, mas com taxas de falhas críticas elevadas (acima de 40.0% na maioria dos pipelines). O *Graph RAG* se destaca com apenas **26.7% de falhas críticas**.")
md.append("- **Médias e Difíceis**: O desempenho sofre um declínio severo. Quase todos os pipelines baseados em múltiplos passos (Standard, Agentic, Hybrid) atingem **100% de taxa de falhas críticas** no nível Médio e Difícil. Isso demonstra a grande limitação de raciocínio do modelo para seguir instruções complexas sob pressão.")
md.append("")
md.append("### C. Comparação entre Pipelines (O Colapso dos Agentes)")
md.append("- **O Colapso dos Pipelines de Múltiplos Passos**: Os pipelines **Standard, Agentic, Hybrid Agent e Fusion RAG** falharam quase integralmente nas dificuldades Média e Difícil. O motivo é que o MedGemma 4b (um modelo menor de 4 bilhões de parâmetros) tem extrema dificuldade em seguir instruções de formatação estruturada (como gerar planos em JSON ou classificar temas). Isso causa falhas de parsing ou escolhas incorretas de seções, resultando em respostas incompletas e irrelevantes que são penalizadas com falha crítica pelo juiz.")
md.append("- **A Resiliência do Naive RAG (Média Geral 0.7384) e Graph RAG (Média Geral 0.7317)**: Como o *Naive RAG* e o *Graph RAG* não dependem de chamadas intermediárias de classificação ou planejamento do LLM, eles mantêm uma recuperação sólida e direta. O Naive RAG obteve o maior Final Score consolidado (**0.7384**) e o Graph RAG a menor taxa consolidada de Falhas Críticas (**48.9%**).")
md.append("")
md.append("---")
md.append("")
md.append("## 6. Conclusão e Recomendações")
md.append("")
md.append("1. **Limitações do MedGemma 4b como Agente**: O MedGemma 4b é inadequado para pipelines de RAG avançados que exigem etapas de raciocínio intermediário (Agentes, Fusion ou Reranking dinâmico). Sua incapacidade de seguir instruções rígidas de planejamento de busca arruína o fluxo RAG.")
md.append("2. **Melhor Escolha Operacional**: Para o MedGemma 4b, deve-se adotar exclusivamente o **Naive RAG** ou o **Graph RAG**. Ambos removem a responsabilidade de tomada de decisão do modelo pequeno na fase de busca, oferecendo maior estabilidade e menor índice de falhas clínicas críticas.")
md.append("3. **Graph RAG como Protetor de Alucinação**: No nível fácil, o Graph RAG reduziu as falhas críticas do modelo para apenas **26.7%**, provando que uma estrutura rígida de relacionamentos de entidades ajuda a guiar o modelo médico de parâmetros reduzidos.")
md.append("")
md.append("---")
md.append("")

with open(local_artifact_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(md))

with open(brain_artifact_path, 'w', encoding='utf-8') as out_f:
    out_f.write("\n".join(md))

print("MedGemma Markdown report successfully generated!")
