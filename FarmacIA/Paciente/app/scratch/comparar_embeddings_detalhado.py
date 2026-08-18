import os
import json
import pandas as pd
from evaluate import load

def calculate_coverage(textos_recuperados_raw, resposta_esperada, rouge_metric):
    if not isinstance(resposta_esperada, str) or not resposta_esperada.strip():
        return 0.0
    
    try:
        chunks = json.loads(textos_recuperados_raw)
        context = " ".join(chunks)
    except Exception:
        context = str(textos_recuperados_raw)
        
    if not context.strip():
        return 0.0
        
    # Calcula ROUGE para ver o quanto da resposta esperada está presente no contexto recuperado
    results = rouge_metric.compute(predictions=[context], references=[resposta_esperada])
    # Retorna o ROUGE-L recall (rougeL)
    return results.get("rougeL", 0.0)

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resultados_dir = os.path.join(base_dir, "resultados")
    
    difficulties = ["faceis", "medias", "dificeis"]
    models = ["all-MiniLM", "BGE"]
    
    rouge = load("rouge")
    
    summary_results = []
    
    print("="*80)
    # Analisa cada combinação de modelo e dificuldade
    for model in models:
        for diff in difficulties:
            filename = f"compare_embeddings_retrieval_{model}_perguntas_respostas_{diff}_output.csv"
            filepath = os.path.join(resultados_dir, filename)
            
            if not os.path.exists(filepath):
                print(f"[Aviso] Arquivo não encontrado: {filename}")
                continue
                
            print(f"Analisando {model} - {diff}...")
            df = pd.read_csv(filepath)
            
            scores = []
            for _, row in df.iterrows():
                score = calculate_coverage(
                    row.get("textos_recuperados", "[]"),
                    row.get("resposta_esperada", ""),
                    rouge
                )
                scores.append(score)
                
            avg_score = sum(scores) / len(scores) if scores else 0.0
            summary_results.append({
                "Modelo": model,
                "Dificuldade": diff.capitalize(),
                "Qtd Perguntas": len(df),
                "Cobertura ROUGE-L (Recall)": round(avg_score, 4)
            })
            
    print("\n" + "="*80)
    print(" RESULTADO DA COMPARAÇÃO DE EMBEDDINGS POR NÍVEL DE DIFICULDADE")
    print("="*80)
    
    df_summary = pd.DataFrame(summary_results)
    
    # Pivotar tabela para facilitar comparação lado a lado
    df_pivot = df_summary.pivot(index="Dificuldade", columns="Modelo", values="Cobertura ROUGE-L (Recall)")
    # Reordenar linhas para Fáceis -> Médias -> Difíceis
    order = ["Faceis", "Medias", "Dificeis"]
    df_pivot = df_pivot.reindex(order)
    
    print(df_pivot.to_markdown())
    print("\n*Nota: A Cobertura ROUGE-L (Recall) mede o percentual de informação do gabarito (resposta esperada) que foi recuperada nos trechos da bula.*")

if __name__ == "__main__":
    main()
