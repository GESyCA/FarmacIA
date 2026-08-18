"""
BulaGraph Demo Script.
Imports a mock leaflet and executes queries representing 7 clinical scenarios.
Displays intent classification, scored evidence chunks, structured answer, and safety warnings.
"""

import os
import sys

# Garante que o diretório atual está no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bulagraph import (
    BulaGraphStore, BulaGraphImporter, BulaGraphRetriever, format_response
)

MOCK_LEAFLET_TEXT = """
IDENTIFICAÇÃO DO MEDICAMENTO
Tylenol (paracetamol 500mg)

1. PARA QUE ESTE MEDICAMENTO É INDICADO?
Este medicamento é indicado em adultos para a redução da febre e para o alívio temporário de dores leves a moderadas, tais como: dores associadas a resfriados comuns, dor de cabeça, dor no corpo, dor de dente, dor nas costas, dores musculares, dores leves associadas a artrites e cólicas menstruais.

3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?
Não use Tylenol se você tem alergia ao paracetamol ou a qualquer componente de sua fórmula.
Este medicamento é contraindicado para pacientes com doença hepática (problemas graves no fígado) ou insuficiência renal.
Não deve ser utilizado por mulheres grávidas (gestantes) ou amamentando (lactantes) sem orientação de um médico ou cirurgião-dentista.
Contraindicado para menores de 12 anos.

5. ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?
Conservar em temperatura ambiente (entre 15 e 30 °C). Proteger da luz e da umidade.
Não use medicamento com o prazo de validade vencido. Guarde-o em sua embalagem original.

6. COMO DEVO USAR ESTE MEDICAMENTO?
Uso oral. Adultos e crianças acima de 12 anos: 1 comprimido de 500mg a 750mg de 4 a 6 horas, conforme a necessidade.
A dose diária máxima recomendada de paracetamol é de 4000mg (8 comprimidos de 500mg) em 24 horas.
Não utilize por mais de 5 dias para dor ou 3 dias para febre sem consultar um médico.

7. O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?
Se você esquecer de tomar uma dose de Tylenol no horário correto, tome-a assim que se lembrar. 
No entanto, se estiver próximo do horário da dose seguinte, pule a dose esquecida e tome a próxima dose no horário planejado. 
Não tome uma dose dobrada (dois comprimidos de uma só vez) para compensar a dose esquecida.

9. O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?
Em caso de superdose ou ingestão acidental de uma quantidade excessiva de paracetamol, procure socorro médico ou um centro de intoxicações imediatamente, mesmo que não haja sintomas aparentes.
O uso de doses muito acima das recomendadas pode causar lesão grave ao fígado (doença hepática severa) e risco de morte. Leve a embalagem do produto.
"""

def run_demo():
    print("=" * 80)
    print("                      DEMONSTRAÇÃO DO BULAGRAPH RAG                      ")
    print("=" * 80)
    
    # 1. Inicializar Store e Importer
    print("\n[1] Inicializando Grafo de Conhecimento...")
    store = BulaGraphStore()
    importer = BulaGraphImporter(store)
    
    # 2. Importar Bula Fictícia
    print("[2] Importando Bula de Tylenol (Mock)...")
    stats = importer.import_leaflet(
        text=MOCK_LEAFLET_TEXT,
        medication_name="Tylenol",
        active_ingredients=["paracetamol"],
        leaflet_type="patient_leaflet",
        source="bula_tylenol_mock.txt"
    )
    
    print("\nEstatísticas do Grafo Gerado:")
    for key, val in stats.items():
        print(f"  - {key}: {val}")
        
    print(f"\nTotal no Store: {store.stats()}")
    
    # 3. Inicializar Retriever
    retriever = BulaGraphRetriever(store)
    
    # 4. Cenários de Consulta de Teste
    cenarios = [
        {
            "id": 1,
            "pergunta": "Para que serve o Tylenol?",
            "descricao": "Indicação Terapêutica"
        },
        {
            "id": 2,
            "pergunta": "Gestante pode tomar esse remédio?",
            "descricao": "Contraindicação para População Sensível (Gestantes)"
        },
        {
            "id": 3,
            "pergunta": "Tenho problemas graves no fígado. Posso tomar?",
            "descricao": "Contraindicação por Condição Clínica (Doença Hepática)"
        },
        {
            "id": 4,
            "pergunta": "Qual a dose diária máxima recomendada para adultos?",
            "descricao": "Posologia e Dosagem"
        },
        {
            "id": 5,
            "pergunta": "O que eu faço se esquecer de tomar um comprimido?",
            "descricao": "Instrução de Dose Esquecida"
        },
        {
            "id": 6,
            "pergunta": "Meu filho tomou uma caixa inteira de paracetamol por acidente! O que fazer?",
            "descricao": "Instrução de Superdosagem (Overdose)"
        },
        {
            "id": 7,
            "pergunta": "Como devo guardar os comprimidos de Tylenol?",
            "descricao": "Condições de Armazenamento"
        }
    ]
    
    print("\n" + "=" * 80)
    print("                         EXECUTANDO CENÁRIOS DE CONSULTA                         ")
    print("=" * 80)
    
    for cenario in cenarios:
        print(f"\nCenário {cenario['id']}: {cenario['descricao']}")
        print(f"Pergunta: '{cenario['pergunta']}'")
        
        # Executa a busca
        result = retriever.retrieve(
            question=cenario["pergunta"],
            medication="Tylenol",
            leaflet_type="patient_leaflet"
        )
        
        # Formata resposta estruturada
        response = format_response(result, max_evidence=2)
        
        print(f"Intenção Classificada: {response['intent'].upper()}")
        print("-" * 40)
        print(f"Resposta Estruturada:\n{response['answer']}")
        print("-" * 40)
        
        if response['evidence']:
            print("Evidências Recuperadas:")
            for idx, ev in enumerate(response['evidence']):
                print(f"  [{idx+1}] Seção: '{ev['section_title']}' (Score: {ev['score']})")
                print(f"      Trecho: \"{ev['text'][:180].strip()}...\"")
        else:
            print("Nenhuma evidência recuperada.")
            
        print(f"Aviso de Segurança: {response['safety_note']}")
        print("-" * 80)

if __name__ == "__main__":
    run_demo()
