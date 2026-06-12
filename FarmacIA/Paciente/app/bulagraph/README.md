# BulaGraph — GraphRAG Leve para Bulas de Medicamentos

Módulo de recuperação estruturada de informações de bulas utilizando grafo de conhecimento com ontologia fechada, otimizado para uso com SLMs locais.

## Conceito

O BulaGraph trata a bula como um **documento regulatório estruturado**, modelando a hierarquia `Medicamento → Bula → Seção → Chunk de Evidência` e as relações clínicas extraídas de cada trecho (contraindicação, interação, reação adversa, etc.).

**Não depende de LLM** para construir o grafo. Utiliza regras, padrões regex e dicionários para extração.

## Instalação

Nenhuma dependência adicional necessária. O módulo utiliza apenas a biblioteca padrão do Python.

## Como Importar uma Bula

```python
from bulagraph import BulaGraphStore, BulaGraphImporter

# 1. Criar o grafo
graph = BulaGraphStore()

# 2. Criar o importador
importer = BulaGraphImporter(graph)

# 3. Importar a bula (texto plain-text ou markdown)
stats = importer.import_leaflet(
    text="""
    1. PARA QUE ESTE MEDICAMENTO É INDICADO?
    Este medicamento é indicado para...
    
    3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?
    Contraindicado para gestantes...
    """,
    medication_name="MeuRemédio",
    active_ingredients=["substância X"],
    leaflet_type="patient_leaflet",
    source="bula_meuremedio.pdf",
)

print(stats)  # Estatísticas de importação
```

## Como Consultar

```python
from bulagraph import BulaGraphRetriever, format_response

# 1. Criar o retriever
retriever = BulaGraphRetriever(graph)

# 2. Fazer uma consulta
result = retriever.retrieve(
    question="Posso usar se estiver grávida?",
    medication="MeuRemédio",
    leaflet_type="patient_leaflet",
)

# 3. Formatar a resposta
response = format_response(result)
print(response["answer"])      # Texto com evidência
print(response["evidence"])    # Lista de trechos citados
print(response["safety_note"]) # Nota de segurança
```

## Como a Ontologia Funciona

### Tipos de Nós (18)
| Tipo | Descrição |
|------|-----------|
| `Medication` | Medicamento |
| `ActiveIngredient` | Princípio ativo |
| `Leaflet` | Bula (paciente ou profissional) |
| `Section` | Seção da bula |
| `EvidenceChunk` | Trecho de texto da bula |
| `Population` | População (gestante, idoso, criança...) |
| `ClinicalCondition` | Condição clínica (doença hepática, renal...) |
| `AdverseEvent` | Evento adverso (diarreia, sonolência...) |
| `InteractingSubstance` | Substância que interage |
| `Recommendation` | Recomendação clínica |
| `Dose` | Dose |
| `AdministrationRoute` | Via de administração |
| `Frequency` | Frequência de uso |
| `StorageCondition` | Condição de armazenamento |
| `MissedDoseInstruction` | Instrução de dose esquecida |
| `OverdoseInstruction` | Instrução de superdose |
| `PatientAction` | Ação do paciente |
| `SafetyWarning` | Alerta de segurança |

### Tipos de Relação (23)
Relações estruturais e clínicas que conectam os nós. Exemplos:
- `CONTRAINDICATED_FOR` — liga EvidenceChunk a Population/Condition
- `INTERACTS_WITH` — liga EvidenceChunk a InteractingSubstance
- `MAY_CAUSE` — liga EvidenceChunk a AdverseEvent
- `STORE_UNDER` — liga EvidenceChunk a StorageCondition

### Perfis de Bula
- `patient_leaflet` — Bula do paciente (9 seções padrão ANVISA)
- `professional_leaflet` — Bula do profissional (10 seções)

## Como Adicionar Novos Sinônimos

```python
from bulagraph import add_synonym

# Adicionar novo par leigo → clínico
add_synonym("remédio para pressão", "anti-hipertensivo")
add_synonym("dor nas juntas", "artralgia")
```

O dicionário pode ser editado diretamente em `bulagraph/normalizer.py` na variável `LAY_TO_CLINICAL`.

## Como Adicionar Novos Padrões de Extração

Edite `bulagraph/extractor.py`:

1. **Novo padrão regex**: Adicione a uma das listas de padrões existentes ou crie uma nova.
2. **Nova entidade no dicionário**: Adicione ao dicionário relevante (`POPULATION_TERMS`, `CONDITION_TERMS`, etc.).
3. **Novo tipo de relação**: Se necessário, adicione o enum em `bulagraph/ontology.py`.

```python
# Exemplo: adicionar detecção de "risco cardiovascular"
CONDITION_TERMS["risco cardiovascular"] = NodeType.CLINICAL_CONDITION
```

## Persistência

```python
# Salvar grafo
graph.save_jsonl("./meu_grafo/")

# Carregar grafo
graph = BulaGraphStore.load_jsonl("./meu_grafo/")
```

## Integração com ChromaDB (Opcional)

O retriever pode combinar busca por grafo com busca vetorial:

```python
retriever = BulaGraphRetriever(graph, vectorstore=meu_vectorstore_chroma)
```

## Executar Testes

```bash
cd FarmacIA/Paciente/app
python -m pytest tests/test_bulagraph.py -v
```

## Executar Demo

```bash
cd FarmacIA/Paciente/app
python bulagraph_demo.py
```
