# FarmacIA — Back-End & RAG Evaluation Framework

Sistema inteligente de recuperação de informações e respostas a perguntas (QA) baseado no conteúdo regulatório de bulas de medicamentos (padrão ANVISA).

O **FarmacIA** implementa e avalia um fluxo experimental rigoroso de **7 arquiteturas RAG (*Retrieval-Augmented Generation*)**, desde abordagens ingênuas até orquestração multi-agente, fusão de rankeamento (*Reciprocal Rank Fusion* + Reranking), recuperação em grafo de conhecimento (*BulaGraph*) e mecanismos de salvaguarda clínica (*Guardrails*).

---

## 📁 Estrutura do Repositório

```
FarmacIA/
├── backend/                       # API Flask e motor dos pipelines RAG
│   ├── bulagraph/                 # Motor do BulaGraph (Knowledge Graph)
│   ├── bulas_markdown/            # Bulas pré-processadas em Markdown
│   ├── bulas_pdf/                 # Bulas oficiais em formato PDF
│   ├── configs/                   # Configurações experimentais em YAML
│   ├── dataset/                   # Datasets de perguntas e respostas
│   ├── eval_deepeval/             # Integração com DeepEval (LLM-as-a-judge)
│   ├── metrics/                   # Métricas customizadas de segurança e fidelidade
│   ├── routes/                    # Endpoints REST (bula_routes, mauq_routes)
│   ├── services/                  # Implementação dos 7 pipelines RAG (pipelines.py)
│   ├── tests/                     # Testes automatizados (pytest)
│   ├── utils/                     # Processamento de texto, vetores e configuração
│   ├── main.py                    # Entry point da API Flask
│   ├── models.py                  # Modelos relacionais (SQLAlchemy)
│   ├── requirements.txt           # Dependências Python do backend
│   ├── rodar_experimentos.py      # Executor principal de experimentos
│   ├── rodar_comparativos.py      # Orquestrador comparativo entre pipelines
│   ├── rodar_comparativo_guarded.py # Comparativo de modelos no pipeline Guarded
│   ├── testar_pergunta_unica.py   # Testador interativo de perguntas
│   ├── testar_compatibilidade_llm.py # Validador de modelos LLM
│   ├── comparar_embeddings.py     # Comparativo de modelos de embedding
│   ├── bulagraph_demo.py          # Demonstração do BulaGraph
│   ├── reconstruir_grafo.py       # Script para reconstruir o grafo
│   └── README.md                  # Documentação detalhada dos pipelines RAG
│
├── frontend/                      # Aplicação móvel e visualização
│   ├── farmacia/                  # Aplicativo mobile em Flutter (paciente)
│   │   ├── lib/                   # Código-fonte Dart (páginas, rotas, widgets, serviços)
│   │   └── pubspec.yaml           # Dependências Flutter
│   ├── view/                      # Interface em React / TypeScript
│   ├── utils/                     # Utilitários complementares
│   ├── Dockerfile                 # Containerização do frontend
│   └── requirements.txt           # Dependências auxiliares
│
├── avaliacao/                     # Resultados e artefatos de avaliação
│   └── resultados/                # CSVs, JSONs e métricas por modelo/pipeline
│       ├── gemma_4_4b/
│       ├── medgemma_4b/
│       ├── mediphi/
│       ├── phi4-mini/
│       ├── Comparativo Guarded/
│       ├── Resultados Compilados/
│       └── graficos/
│
├── dataset/                       # Datasets de referência e ground truth
│   ├── dificeis_revisadas.csv
│   ├── medias_revisadas.csv
│   ├── faceis_revisadas.csv
│   └── retrival_ground_truth/     # Ground truth de recuperação por chunks
│
├── docs/                          # Documentação e figuras
│   └── figuras/                   # Diagramas dos pipelines
│
├── legado/                        # [NÃO SINCRONIZADO] Arquivos e modelos legados
├── .env.example                   # Template de variáveis de ambiente
├── .gitignore                     # Regras de segurança e exclusão de binários
└── pyproject.toml
```

---

## 🚀 Instalação e Configuração

### 1. Pré-requisitos
- **Python 3.10+** (recomendado Python 3.11 ou 3.12)
- **Flutter SDK 3.x+** (para o aplicativo móvel `frontend/farmacia`)
- **Node.js 18+** (para `frontend/view`, se aplicável)
- **Ollama** (para execução de modelos LLM locais)

### 2. Clonar e Configurar Ambiente Virtual

```bash
# Clonar o repositório da organização GESyCA
git clone https://github.com/GESyCA/FarmacIA.git
cd FarmacIA

# Criar e ativar o ambiente virtual
python -m venv .venv

# No Windows (PowerShell):
.venv\Scripts\Activate.ps1

# No Linux/macOS:
source .venv/bin/activate

# Instalar as dependências do backend
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Configurar Variáveis de Ambiente

Copie o arquivo template `.env.example` na raiz do projeto para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
# Chave da API Google Gemini (usada como Juiz LLM e em pipelines cloud)
GOOGLE_API_KEY="sua-chave-google-aqui"

# Chave OpenRouter (opcional, para modelos cloud adicionais)
OPEN_ROUTER_API_KEY="sua-chave-openrouter-aqui"

# Chave Groq (opcional, para inferência de alta velocidade)
GROQ_API_KEY="sua-chave-groq-aqui"

# Chave HuggingFace (opcional, para download de modelos/datasets)
HF_APY_KEY="sua-chave-huggingface-aqui"

# Desabilitar telemetria
ANONYMIZED_TELEMETRY=False
```

---

## 🗄️ Reprodutibilidade: Banco Vetorial, Grafo e Modelos

Por questões de segurança e boas práticas, arquivos binários pesados (bancos SQLite, ChromaDB e pesos de modelos) não são versionados no Git. Siga os passos abaixo para recriá-los:

### 1. Gerar a Base Vetorial (ChromaDB)
Ao rodar qualquer pipeline pela primeira vez, o ChromaDB processa e indexa os PDFs das bulas automaticamente. Para forçar a recriação via experimento:
- No arquivo YAML desejado (`backend/configs/*.yaml`), defina `generate_vector_db: true`.
- Ou execute diretamente:
```bash
cd backend
python utils/calibrar_threshold.py
```

### 2. Reconstruir o Grafo de Conhecimento (*BulaGraph*)
Para gerar a base do grafo (`nodes.jsonl`, `edges.jsonl`, `leaflets.jsonl`, `sections.jsonl`, `chunks.jsonl`):
```bash
cd backend
python reconstruir_grafo.py
```
Os arquivos serão gerados em `backend/instance/bulagraph_store/`.

### 3. Instalar Modelos Locais via Ollama
Para reproduzir os experimentos locais com modelos médicos e gerais:

```bash
# Modelos avaliados no benchmark
ollama pull phi4-mini
ollama pull gemma:4b
ollama pull qwen2.5:3b

# Modelos médicos (disponíveis no Ollama Hub)
ollama pull medgemma:4b
```

---

## 🔬 Experimentos RAG & Os 7 Pipelines Avaliados

> 📖 **Documentação Completa dos 7 Pipelines:**  
> A especificação detalhada de arquitetura, system prompts, formulação teórica, ontologia BulaGraph, métricas de avaliação e detalhes de cada um dos 7 pipelines RAG está documentada em:  
> 🔗 **[`backend/README.md`](backend/README.md)**

### Visão Geral dos 7 Pipelines RAG

| # | Pipeline | Descrição Resumida |
|---|---|---|
| **1** | **Standard RAG** | Busca densa (vetorial) padrão com filtro prévio por medicamento e similaridade de cosseno. |
| **2** | **Agentic RAG** | Agente de planejamento de consulta que classifica a intenção clínica e restringe a busca às seções regulatórias exatas. |
| **3** | **Hybrid Agentic RAG** | Combina roteamento por seções com recuperação dinâmica adaptativa: seções curtas são injetadas integralmente; seções longas usam busca densa. |
| **4** | **Fusion RAG** | Fusão de busca densa (vetorial) + busca léxica (BM25) via algoritmo **RRF** (*Reciprocal Rank Fusion*, $k=60$) com posterior **Reranking** neural (*CrossEncoder* `bge-reranker-base`). |
| **5** | **Graph RAG (BulaGraph)** | Recuperação estruturada sobre grafo de conhecimento regulatório de 18 tipos de nós e 23 tipos de relações clínicas. |
| **6** | **Naive RAG** | Baseline de busca vetorial direta sem enriquecimento de metadados ou restrição de escopo. |
| **7** | **Guarded Hybrid Agentic Fusion RAG** | Arquitetura unificada de produção: integra agente de planejamento, expansão determinística de segurança, busca híbrida (Dense + BM25), RRF, Reranker e *Guardrails* de confiança clínica. |

Para ler os prompts de sistema, diagramas e detalhes operacionais de cada pipeline, consulte o **[`backend/README.md`](backend/README.md)**.

---

## 💻 Como Rodar os Experimentos

### 1. Rodar um Experimento Individual (via YAML)
```bash
cd backend
python rodar_experimentos.py --config configs/exp_compare_07_guarded.yaml
```

### 2. Rodar o Comparativo Completo dos 7 Pipelines
```bash
cd backend
python rodar_comparativos.py
```

### 3. Testar uma Pergunta Específica Interativamente
```bash
cd backend
python testar_pergunta_unica.py --medicamento "AMOXIL" --pergunta "Quais são as contraindicações do Amoxil?"
```

### 4. Validar Compatibilidade de um Modelo LLM
```bash
cd backend
python testar_compatibilidade_llm.py
```

---

## 🌐 Executar a API Back-End (Flask)

Para iniciar o servidor da API REST:

```bash
cd backend
python main.py
```

A API estará disponível em `http://localhost:5000` com os seguintes endpoints:

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/` | Health check da API |
| `POST` | `/perguntar` | Envia uma pergunta sobre medicamento e recebe a resposta do RAG |
| `POST` | `/topicos` | Classifica os tópicos da pergunta em relação à bula |
| `POST` | `/feedback` | Registra avaliação do usuário sobre a resposta (score 1-5 e comentário) |
| `GET` | `/questoes` | Retorna as questões do questionário MAUQ (usabilidade móvel) |
| `POST` | `/responder` | Processa e calcula os scores de usabilidade MAUQ |

---

## 📱 Executar o Front-End (Flutter & React)

### Aplicativo Mobile Flutter (`frontend/farmacia`)
O aplicativo móvel do paciente é desenvolvido em Flutter e se conecta à API REST do backend.

```bash
cd frontend/farmacia

# Baixar as dependências do Flutter
flutter pub get

# Executar em emulador ou dispositivo conectado
flutter run
```

### Visualização / Interface Web (`frontend/view`)
```bash
cd frontend/view

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento
npm start
```

---

## 🛡️ Auditoria de Segurança & Privacidade

- **Proteção de Credenciais:** O arquivo `.env` e chaves de API estão permanentemente excluídos do versionamento através do `.gitignore`.
- **Exclusão de Dados Pessoais e Binários:** Bancos de dados (`*.db`, `*.sqlite3`), diretórios `instance/`, `chroma_bulas/` e pesos de modelos (`*.safetensors`, `*.gguf`, `*.bin`) são mantidos exclusivamente locais.
- **Pasta Legado Isolada:** A pasta `legado/` armazena ferramentas de terceiros e arquivos históricos sem sincronização com o GitHub.
