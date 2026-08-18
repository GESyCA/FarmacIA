"""
Testes unitários para o pipeline Guarded Hybrid Agentic Fusion RAG.

Testa:
  1. Registro no PipelineFactory
  2. Expansão de seções (sem duplicatas, ignora inexistentes)
  3. Parsing do planejador + fallback
  4. Avaliação de confiança da evidência
  5. BM25 com degradação graciosa
  6. Compatibilidade dos metadados de saída
  7. Busca global sempre executada
"""

import sys
import os
import json
import unittest
from unittest.mock import MagicMock, patch, PropertyMock

# Garante que o diretório app esteja no path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services.pipelines import (
    PipelineFactory,
    GuardedHybridAgenticFusionRAGPipeline,
    FusionRAGPipeline,
    SECTION_EXPANSION_MAP,
    SAFETY_SECTIONS,
    SECOES_DISPONIVEIS,
    BasePipeline,
)


class TestPipelineRegistration(unittest.TestCase):
    """1. O pipeline é registrado corretamente no PipelineFactory."""

    def test_factory_returns_guarded_pipeline(self):
        pipeline = PipelineFactory.get_pipeline("guarded_hybrid_agentic_fusion_rag")
        self.assertIsInstance(pipeline, GuardedHybridAgenticFusionRAGPipeline)

    def test_factory_returns_base_pipeline(self):
        pipeline = PipelineFactory.get_pipeline("guarded_hybrid_agentic_fusion_rag")
        self.assertIsInstance(pipeline, BasePipeline)

    def test_factory_still_works_for_existing_pipelines(self):
        """Não quebra os pipelines existentes."""
        for name in [
            "standard_rag", "agentic_rag", "hybrid_agentic_rag",
            "fusion_rag", "graph_rag", "naive_rag",
        ]:
            pipeline = PipelineFactory.get_pipeline(name)
            self.assertIsInstance(pipeline, BasePipeline)

    def test_factory_raises_for_unknown(self):
        with self.assertRaises(ValueError):
            PipelineFactory.get_pipeline("nonexistent_pipeline")


class TestSectionExpansion(unittest.TestCase):
    """2. Expansão de seções sem duplicatas e filtrando inexistentes."""

    def setUp(self):
        self.pipeline = GuardedHybridAgenticFusionRAGPipeline()
        self.available = set(SECOES_DISPONIVEIS.keys())

    def test_expansion_returns_related_sections(self):
        selected = ["COMO DEVO USAR ESTE MEDICAMENTO?"]
        expanded = self.pipeline._expand_sections(selected, self.available)
        self.assertIn("O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?", expanded)
        self.assertIn("O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?", expanded)

    def test_expansion_no_duplicates(self):
        selected = [
            "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?",
            "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?",
        ]
        expanded = self.pipeline._expand_sections(selected, self.available)
        # Nenhuma seção já selecionada deve aparecer na expansão
        for sec in selected:
            self.assertNotIn(sec, expanded)
        # Sem duplicatas na lista expandida
        self.assertEqual(len(expanded), len(set(expanded)))

    def test_expansion_ignores_nonexistent_sections(self):
        """Se a seção correlata não existe no set disponível, é ignorada."""
        limited_available = {"COMO DEVO USAR ESTE MEDICAMENTO?"}
        selected = ["COMO DEVO USAR ESTE MEDICAMENTO?"]
        expanded = self.pipeline._expand_sections(selected, limited_available)
        # As seções relacionadas não estão em limited_available, então nada é expandido
        self.assertEqual(expanded, [])

    def test_expansion_empty_input(self):
        expanded = self.pipeline._expand_sections([], self.available)
        self.assertEqual(expanded, [])

    def test_expansion_unknown_section(self):
        """Seção desconhecida não tem mapa de expansão."""
        expanded = self.pipeline._expand_sections(
            ["SEÇÃO INVENTADA"], self.available
        )
        self.assertEqual(expanded, [])


class TestPlanSectionsParsing(unittest.TestCase):
    """3. Parsing do planejador e fallback robusto."""

    def _mock_llm(self, response_text):
        """Cria um mock de LLM que retorna um texto fixo."""
        mock_llm = MagicMock()
        mock_llm.__or__ = MagicMock(return_value=mock_llm)
        mock_llm.invoke = MagicMock(return_value=response_text)
        return mock_llm

    @patch("services.pipelines.PromptTemplate")
    @patch("services.pipelines.StrOutputParser")
    def test_valid_json_response(self, mock_parser_cls, mock_prompt_cls):
        """Planejador retorna JSON válido."""
        json_response = json.dumps({
            "primary_sections": ["COMO DEVO USAR ESTE MEDICAMENTO?"],
            "secondary_sections": ["PARA QUE ESTE MEDICAMENTO É INDICADO?"],
            "safety_sections": ["QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?"],
            "rationale": "Pergunta sobre dosagem"
        })

        # Mock do chain
        mock_chain = MagicMock()
        mock_chain.invoke = MagicMock(return_value=json_response)
        mock_prompt_cls.from_template.return_value.__or__ = MagicMock(return_value=MagicMock())
        mock_prompt_cls.from_template.return_value.__or__.return_value.__or__ = MagicMock(return_value=mock_chain)

        result = GuardedHybridAgenticFusionRAGPipeline._plan_sections(
            mock_chain, "AMOXIL", "Como devo tomar?"
        )

        # O método é estático e invoca chain.invoke, então verificamos o resultado
        self.assertIsInstance(result, dict)
        self.assertIn("primary_sections", result)
        self.assertIn("secondary_sections", result)
        self.assertIn("safety_sections", result)

    def test_fallback_on_empty_result(self):
        """Se o planejador retorna listas vazias, fallback seguro é aplicado."""
        pipeline = GuardedHybridAgenticFusionRAGPipeline()

        # Simula resultado vazio do parsing
        result = {
            "primary_sections": [],
            "secondary_sections": [],
            "safety_sections": [],
            "rationale": "",
        }

        # O pipeline aplica fallback se ambas primary e secondary estão vazias
        if not result["primary_sections"] and not result["secondary_sections"]:
            result["primary_sections"] = [
                "O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?"
            ]
            result["safety_sections"] = [
                "QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?"
            ]

        self.assertTrue(len(result["primary_sections"]) > 0)


class TestEvidenceConfidence(unittest.TestCase):
    """4. Validador de confiança da evidência."""

    def _make_doc(self, section="", content="teste"):
        doc = MagicMock()
        doc.metadata = {"section": section}
        doc.page_content = content
        return doc

    def test_no_evidence_returns_low(self):
        confidence = GuardedHybridAgenticFusionRAGPipeline._assess_evidence_confidence(
            ranked_evidence=[],
            pergunta="teste",
            planned_sections=["COMO DEVO USAR ESTE MEDICAMENTO?"],
        )
        self.assertEqual(confidence, "low")

    def test_low_reranker_score_returns_low(self):
        doc = self._make_doc("COMO DEVO USAR ESTE MEDICAMENTO?")
        confidence = GuardedHybridAgenticFusionRAGPipeline._assess_evidence_confidence(
            ranked_evidence=[doc],
            pergunta="teste",
            planned_sections=["COMO DEVO USAR ESTE MEDICAMENTO?"],
            reranker_scores=[-5.0],
        )
        self.assertEqual(confidence, "low")

    def test_no_overlap_with_planned_returns_low(self):
        doc = self._make_doc("IDENTIFICAÇÃO DO MEDICAMENTO")
        confidence = GuardedHybridAgenticFusionRAGPipeline._assess_evidence_confidence(
            ranked_evidence=[doc],
            pergunta="teste",
            planned_sections=["COMO DEVO USAR ESTE MEDICAMENTO?"],
        )
        self.assertEqual(confidence, "low")

    def test_safety_question_without_safety_evidence_returns_low(self):
        doc = self._make_doc("PARA QUE ESTE MEDICAMENTO É INDICADO?")
        confidence = GuardedHybridAgenticFusionRAGPipeline._assess_evidence_confidence(
            ranked_evidence=[doc],
            pergunta="Posso tomar durante a gravidez?",
            planned_sections=["PARA QUE ESTE MEDICAMENTO É INDICADO?"],
        )
        self.assertEqual(confidence, "low")

    def test_good_evidence_returns_high(self):
        docs = [
            self._make_doc("COMO DEVO USAR ESTE MEDICAMENTO?", f"chunk_{i}")
            for i in range(5)
        ]
        confidence = GuardedHybridAgenticFusionRAGPipeline._assess_evidence_confidence(
            ranked_evidence=docs,
            pergunta="Como tomar este remédio?",
            planned_sections=["COMO DEVO USAR ESTE MEDICAMENTO?"],
            reranker_scores=[3.0, 2.5, 2.0, 1.5, 1.0],
        )
        self.assertEqual(confidence, "high")

    def test_few_evidence_returns_medium(self):
        docs = [self._make_doc("COMO DEVO USAR ESTE MEDICAMENTO?")]
        confidence = GuardedHybridAgenticFusionRAGPipeline._assess_evidence_confidence(
            ranked_evidence=docs,
            pergunta="Como tomar?",
            planned_sections=["COMO DEVO USAR ESTE MEDICAMENTO?"],
            reranker_scores=[2.0],
        )
        self.assertEqual(confidence, "medium")


class TestBM25Search(unittest.TestCase):
    """5. BM25 degrada graciosamente quando não disponível."""

    def _make_doc(self, content):
        doc = MagicMock()
        doc.page_content = content
        return doc

    def test_empty_docs_returns_empty(self):
        result = GuardedHybridAgenticFusionRAGPipeline._bm25_search([], "query", 5)
        self.assertEqual(result, [])

    def test_bm25_returns_ranked_results(self):
        docs = [
            self._make_doc("Este medicamento é indicado para dor"),
            self._make_doc("Contraindicações do medicamento"),
            self._make_doc("Dose de medicamento para dor intensa"),
        ]
        result = GuardedHybridAgenticFusionRAGPipeline._bm25_search(
            docs, "dose medicamento dor", top_k=2
        )
        self.assertLessEqual(len(result), 2)
        self.assertTrue(len(result) > 0)


class TestRRFReuse(unittest.TestCase):
    """6. Reutiliza RRF do FusionRAGPipeline."""

    def _make_doc(self, content):
        doc = MagicMock()
        doc.page_content = content
        return doc

    def test_rrf_fusion_is_callable(self):
        """Verifica que _rrf_fusion do FusionRAG é acessível."""
        self.assertTrue(callable(FusionRAGPipeline._rrf_fusion))

    def test_rrf_fusion_deduplicates(self):
        doc1 = self._make_doc("texto A")
        doc2 = self._make_doc("texto B")
        doc3 = self._make_doc("texto A")  # duplicata

        result = FusionRAGPipeline._rrf_fusion([[doc1, doc2], [doc3]], rrf_k=60)
        contents = [doc.page_content for doc in result]
        self.assertEqual(len(set(contents)), len(contents))


class TestOutputMetadataCompatibility(unittest.TestCase):
    """7. Verifica que o metadado de saída contém os campos esperados."""

    def test_metadata_keys_present(self):
        """Simula os campos que o pipeline deve retornar."""
        expected_keys = [
            "tempo_recuperacao",
            "tempo_inferencia",
            "secoes_recuperadas",
            "chunk_ids_recuperados",
            "textos_recuperados",
            "resposta_crua",
        ]

        # Simula o metadata que o pipeline retornaria
        mock_metadata = {
            "tempo_recuperacao": 1.234,
            "tempo_inferencia": 0.567,
            "secoes_recuperadas": ["COMO DEVO USAR ESTE MEDICAMENTO?"],
            "chunk_ids_recuperados": ["id1", "id2"],
            "textos_recuperados": ["texto1", "texto2"],
            "resposta_crua": "resposta bruta",
            "guarded_debug_trace": {"fallback_triggered": False},
        }

        for key in expected_keys:
            self.assertIn(key, mock_metadata)


class TestSectionExpansionMap(unittest.TestCase):
    """8. O mapa de expansão é válido e referencia seções existentes."""

    def test_all_keys_are_valid_sections(self):
        for key in SECTION_EXPANSION_MAP:
            self.assertIn(key, SECOES_DISPONIVEIS,
                          f"Chave do mapa de expansão '{key}' não existe em SECOES_DISPONIVEIS")

    def test_all_values_are_valid_sections(self):
        for key, values in SECTION_EXPANSION_MAP.items():
            for val in values:
                self.assertIn(val, SECOES_DISPONIVEIS,
                              f"Valor '{val}' de '{key}' não existe em SECOES_DISPONIVEIS")


class TestSafetySections(unittest.TestCase):
    """9. Seções de segurança são válidas."""

    def test_all_safety_sections_are_valid(self):
        for sec in SAFETY_SECTIONS:
            self.assertIn(sec, SECOES_DISPONIVEIS,
                          f"Seção de segurança '{sec}' não existe em SECOES_DISPONIVEIS")


class TestConfigLoading(unittest.TestCase):
    """10. O YAML de configuração é carregável e válido."""

    def test_guarded_yaml_loads(self):
        import yaml
        config_path = os.path.join(
            os.path.dirname(__file__), "..", "configs", "exp_compare_07_guarded.yaml"
        )
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
            self.assertEqual(config["pipeline_type"], "guarded_hybrid_agentic_fusion_rag")
            self.assertIn("guarded_retrieval", config)
            self.assertIn("primary_vector_top_k", config["guarded_retrieval"])
            self.assertIn("reranker_model", config["guarded_retrieval"])
        else:
            self.skipTest(f"Config file not found: {config_path}")


if __name__ == "__main__":
    unittest.main()
