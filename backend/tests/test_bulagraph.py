"""
Unit tests for BulaGraph module.
Covers ontology, normalizer, store, extractor, importer, retriever (v2), and formatter.
"""

import os
import shutil
import tempfile
import unittest
import sys

# Garante que o diretório atual está no path
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")

from bulagraph import (
    BulaGraphStore, BulaGraphImporter, BulaGraphRetriever, format_response,
    NodeType, RelationType, SectionType, LeafletType, QueryIntent,
    normalize_entity, normalize_text, add_synonym,
    IntentCandidate, SectionCandidate, RetrievalPlan, QueryUnderstanding,
)


class TestBulaGraphOntology(unittest.TestCase):
    """Testes para garantir integridade e regras da Ontologia."""

    def test_enums_exist(self):
        self.assertEqual(NodeType.MEDICATION.value, "Medication")
        self.assertEqual(RelationType.INDICATED_FOR.value, "INDICATED_FOR")
        self.assertEqual(SectionType.INDICATION.value, "indication")
        self.assertEqual(LeafletType.PATIENT.value, "patient_leaflet")
        self.assertEqual(QueryIntent.INDICATION.value, "indication")


class TestBulaGraphNormalizer(unittest.TestCase):
    """Testes para normalização de linguagem leiga → clínica."""

    def test_normalize_entity(self):
        self.assertEqual(normalize_entity("problemas no fígado"), "doença hepática")
        self.assertEqual(normalize_entity("grávida"), "gestante")
        self.assertEqual(normalize_entity("enjoo"), "náusea")
        # Mantém termo desconhecido
        self.assertEqual(normalize_entity("dor no dedão"), "dor no dedão")

    def test_normalize_text(self):
        text = "Se você tem problemas no fígado ou está grávida, cuidado."
        normalized = normalize_text(text)
        self.assertIn("doença hepática", normalized)
        self.assertIn("gestante", normalized)

    def test_add_synonym(self):
        add_synonym("dor de dente", "odontalgia")
        self.assertEqual(normalize_entity("dor de dente"), "odontalgia")


class TestBulaGraphStore(unittest.TestCase):
    """Testes do Grafo In-memory com persistência JSONL."""

    def setUp(self):
        self.store = BulaGraphStore()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_crud_nodes_edges(self):
        # Add nodes
        med_id = self.store.add_node(NodeType.MEDICATION, "Paracetamol")
        cond_id = self.store.add_node(NodeType.CLINICAL_CONDITION, "Doença hepática")

        self.assertIsNotNone(med_id)
        self.assertIsNotNone(cond_id)

        # Find node
        found_id = self.store.find_node("Paracetamol")
        self.assertEqual(found_id, med_id)

        # Add edge
        edge_id = self.store.add_edge(med_id, cond_id, RelationType.CONTRAINDICATED_FOR)
        self.assertIsNotNone(edge_id)

        # Get neighbors
        neighbors = self.store.get_neighbors(med_id, "outgoing")
        self.assertEqual(len(neighbors), 1)
        self.assertEqual(neighbors[0]["node"]["id"], cond_id)
        self.assertEqual(neighbors[0]["edge"]["type"], "CONTRAINDICATED_FOR")

    def test_jsonl_persistence(self):
        med_id = self.store.add_node(NodeType.MEDICATION, "Clonazepam")
        cond_id = self.store.add_node(NodeType.CLINICAL_CONDITION, "Apneia do sono")
        self.store.add_edge(med_id, cond_id, RelationType.CONTRAINDICATED_FOR)

        # Save
        self.store.save_jsonl(self.temp_dir)

        # Load
        new_store = BulaGraphStore.load_jsonl(self.temp_dir)
        self.assertEqual(len(new_store.nodes), 2)
        self.assertEqual(len(new_store.edges), 1)

        new_med_id = new_store.find_node("Clonazepam")
        self.assertEqual(new_med_id, med_id)


class TestBulaGraphExtractionAndImport(unittest.TestCase):
    """Testes da extração rule-based e importador."""

    def test_import_and_extract(self):
        store = BulaGraphStore()
        importer = BulaGraphImporter(store)

        leaflet_text = """
        IDENTIFICAÇÃO DO MEDICAMENTO
        Nome: Tylenol (paracetamol)

        1. PARA QUE ESTE MEDICAMENTO É INDICADO?
        Este medicamento é indicado para o alívio temporário de dores leves a moderadas.

        3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?
        Não use Tylenol se você tem alergia ao paracetamol ou se tem problemas no fígado.

        5. ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?
        Conservar em temperatura ambiente (entre 15 e 30 °C). Proteger da luz e umidade.

        6. COMO DEVO USAR ESTE MEDICAMENTO?
        Tomar 1 comprimido a cada 6 horas.

        7. O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?
        Se você esquecer de tomar uma dose, tome-a assim que lembrar. Não tome dose dobrada.

        9. O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?
        Em caso de superdose, procure socorro médico imediatamente para evitar danos no fígado.
        """

        stats = importer.import_leaflet(
            text=leaflet_text,
            medication_name="Tylenol",
            active_ingredients=["paracetamol"],
            leaflet_type="patient_leaflet",
            source="mock_leaflet.txt",
        )

        self.assertGreater(stats["sections_found"], 0)
        self.assertGreater(stats["chunks_created"], 0)
        self.assertGreater(stats["nodes_created"], 0)
        self.assertGreater(stats["edges_created"], 0)

        # Verifica se nós específicos foram criados
        self.assertIsNotNone(store.find_node("Tylenol", NodeType.MEDICATION))
        self.assertIsNotNone(store.find_node("paracetamol", NodeType.ACTIVE_INGREDIENT))
        self.assertIsNotNone(store.find_node("doença hepática", NodeType.CLINICAL_CONDITION))


class TestBulaGraphRetrieverAndFormatter(unittest.TestCase):
    """Testes para o retriever por intenção e formatador."""

    @classmethod
    def setUpClass(cls):
        cls.store = BulaGraphStore()
        cls.importer = BulaGraphImporter(cls.store)

        cls.leaflet_text = """
        IDENTIFICAÇÃO DO MEDICAMENTO
        Tylenol (paracetamol)

        1. PARA QUE ESTE MEDICAMENTO É INDICADO?
        Indicado para redução da febre e alívio temporário de dores leves a moderadas.

        3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?
        Não use se você tem alergia ao paracetamol ou se tem problemas no fígado grave.
        Contraindicado na gravidez e para menores de 12 anos.

        5. ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?
        Conservar em temperatura ambiente (entre 15 e 30 °C). Proteger da luz.

        6. COMO DEVO USAR ESTE MEDICAMENTO?
        Adultos: 1 comprimido de 500mg a 750mg de 4 a 6 horas.

        7. O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?
        Se você esquecer de tomar, tome assim que lembrar. Não dobre a dose.

        9. O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?
        Em caso de superdose ou ingestão excessiva acidental, procure socorro médico imediatamente.
        """

        cls.importer.import_leaflet(
            text=cls.leaflet_text,
            medication_name="Tylenol",
            active_ingredients=["paracetamol"],
            leaflet_type="patient_leaflet",
            source="mock_tylenol.txt",
        )

        cls.retriever = BulaGraphRetriever(cls.store)

    def test_intent_classification_legacy(self):
        """Testa que o wrapper _classify_intent (backward-compatible) ainda funciona."""
        intent = self.retriever._classify_intent("Como devo tomar o paracetamol?")
        self.assertEqual(intent, QueryIntent.DOSAGE)

        intent = self.retriever._classify_intent("Quais as contraindicações do Tylenol?")
        self.assertEqual(intent, QueryIntent.CONTRAINDICATION)

        intent = self.retriever._classify_intent("Posso tomar grávida?")
        self.assertEqual(intent, QueryIntent.PREGNANCY_LACTATION)

    def test_multi_intent_classification(self):
        """Testa a nova classificação de múltiplas intenções."""
        candidates = self.retriever._classify_intents(
            "Posso tomar grávida?", entities=[]
        )
        self.assertIsInstance(candidates, list)
        self.assertGreater(len(candidates), 0)
        self.assertIsInstance(candidates[0], IntentCandidate)
        self.assertEqual(candidates[0].intent, QueryIntent.PREGNANCY_LACTATION)
        self.assertGreater(candidates[0].confidence, 0.0)

    def test_retrieval_scenarios(self):
        # 1. Indicação
        res = self.retriever.retrieve("Para que serve o Tylenol?", medication="Tylenol")
        self.assertEqual(res.intent, "indication")
        self.assertGreater(len(res.evidence), 0)
        self.assertIn("febre", res.evidence[0].text.lower())

        # 2. Contraindicação por entidade (população gestante)
        res = self.retriever.retrieve("Posso tomar grávida?", medication="Tylenol")
        self.assertEqual(res.intent, "pregnancy_lactation")
        self.assertGreater(len(res.evidence), 0)

        # 3. Superdose
        res = self.retriever.retrieve("O que fazer se tomar muito comprimido?", medication="Tylenol")
        self.assertEqual(res.intent, "overdose")
        self.assertGreater(len(res.evidence), 0)

    def test_retrieval_result_has_new_fields(self):
        """Testa que o RetrievalResult inclui os novos campos."""
        res = self.retriever.retrieve("Para que serve?", medication="Tylenol")
        self.assertIsNotNone(res.query_understanding)
        self.assertIsInstance(res.confidence, dict)
        self.assertIn("intent_confidence", res.confidence)
        self.assertIn("retrieval_confidence", res.confidence)
        self.assertIn("answer_confidence", res.confidence)

    def test_debug_mode(self):
        """Testa que debug=True inclui informações extras."""
        res = self.retriever.retrieve(
            "Para que serve o Tylenol?", medication="Tylenol", debug=True
        )
        self.assertIsInstance(res.debug, dict)
        self.assertIn("candidate_counts", res.debug)
        self.assertIn("retrieval_plan", res.debug)
        self.assertIn("intent_candidates", res.debug)
        self.assertIn("confidence", res.debug)
        self.assertIn("top_evidence", res.debug)

    def test_debug_false_no_debug_data(self):
        """Testa que debug=False não popula o campo debug."""
        res = self.retriever.retrieve(
            "Para que serve o Tylenol?", medication="Tylenol", debug=False
        )
        self.assertEqual(res.debug, {})

    def test_formatter(self):
        res = self.retriever.retrieve("Posso usar grávida?", medication="Tylenol")
        formatted = format_response(res)

        self.assertIn("answer", formatted)
        self.assertIn("safety_note", formatted)
        self.assertIn("evidence", formatted)

        # Safety Note deve conter o aviso para buscar profissional para consultas de alto risco (pregnancy)
        self.assertIn("orientação médica ou farmacêutica", formatted["safety_note"])
        self.assertIn("consultar um profissional", formatted["safety_note"])

        # Deve ter citado evidência
        self.assertGreater(len(formatted["evidence"]), 0)
        self.assertEqual(formatted["evidence"][0]["section_type"], "contraindication")

    def test_no_evidence_no_claim(self):
        # Testa quando não encontra evidência para uma medicação inexistente
        res = self.retriever.retrieve("Qual a dose recomendada?", medication="Inexistente")
        formatted = format_response(res)
        self.assertIn("não foi encontrado trecho suficiente", formatted["answer"])
        self.assertEqual(len(formatted["evidence"]), 0)


class TestBulaGraphRetrieverV2Scenarios(unittest.TestCase):
    """
    Cenários de teste específicos para o retriever v2 (Intent-Aware / Section-Aware).
    Validam multi-intent, estratégias do plano e seções esperadas.
    """

    @classmethod
    def setUpClass(cls):
        cls.store = BulaGraphStore()
        cls.importer = BulaGraphImporter(cls.store)

        cls.leaflet_text = """
        IDENTIFICAÇÃO DO MEDICAMENTO
        Dipirona monoidratada

        1. PARA QUE ESTE MEDICAMENTO É INDICADO?
        Este medicamento é indicado como analgésico e antitérmico para dores e febre.

        3. QUANDO NÃO DEVO USAR ESTE MEDICAMENTO?
        Não use se você tem alergia à dipirona ou pirazolonas.
        Contraindicado para gestantes no primeiro e terceiro trimestres.
        Pacientes com problemas no fígado grave devem evitar o uso.

        4. O QUE DEVO SABER ANTES DE USAR ESTE MEDICAMENTO?
        Pacientes com doença hepática ou renal devem ser monitorados.
        Cuidado ao usar com anticoagulantes. Pode causar queda de pressão.
        Não use junto com metotrexato.
        Dipirona interage com varfarina, aumentando o risco de sangramento.
        Quem tem problema no fígado deve ser acompanhado durante o uso.
        Uso com álcool pode potencializar efeitos colaterais.

        5. ONDE, COMO E POR QUANTO TEMPO POSSO GUARDAR ESTE MEDICAMENTO?
        Conservar em temperatura ambiente (entre 15 e 30 °C).

        6. COMO DEVO USAR ESTE MEDICAMENTO?
        Adultos: 1 comprimido de 500mg a 1000mg até 4 vezes ao dia.
        Modo de uso: via oral com água.

        7. O QUE DEVO FAZER QUANDO EU ME ESQUECER DE USAR ESTE MEDICAMENTO?
        Se esquecer de tomar uma dose, tome assim que lembrar.

        8. QUAIS OS MALES QUE ESTE MEDICAMENTO PODE ME CAUSAR?
        Pode causar sonolência, tontura, náusea e reações alérgicas.
        Esse remédio dá sono em alguns pacientes.
        Reações adversas incluem queda de pressão e agranulocitose.

        9. O QUE FAZER SE ALGUÉM USAR UMA QUANTIDADE MAIOR DO QUE A INDICADA DESTE MEDICAMENTO?
        Em caso de superdose, procure socorro médico.
        """

        cls.importer.import_leaflet(
            text=cls.leaflet_text,
            medication_name="Dipirona",
            active_ingredients=["dipirona monoidratada"],
            leaflet_type="patient_leaflet",
            source="mock_dipirona.txt",
        )

        cls.retriever = BulaGraphRetriever(cls.store)

    # ------------------------------------------------------------------
    # Cenário 1: Pergunta clara de interação
    # ------------------------------------------------------------------
    def test_scenario_1_clear_interaction(self):
        """'Dipirona interage com varfarina?' → INTERACTION, graph_focused ou graph_hybrid_restricted."""
        res = self.retriever.retrieve(
            "Dipirona interage com varfarina?",
            medication="Dipirona",
            debug=True,
        )

        # Intenção primária deve ser INTERACTION
        self.assertEqual(res.intent, "interaction")

        # Múltiplas intenções: a principal deve ser INTERACTION
        qu = res.query_understanding
        self.assertIsNotNone(qu)
        top_intents = [c.intent for c in qu.intent_candidates]
        self.assertIn(QueryIntent.INTERACTION, top_intents)

        # Estratégia deve ser graph_focused ou graph_hybrid_restricted
        strategy = qu.retrieval_plan.strategy
        self.assertIn(strategy, {"graph_focused", "graph_hybrid_restricted"})

        # Deve ter evidência
        self.assertGreater(len(res.evidence), 0)

    # ------------------------------------------------------------------
    # Cenário 2: Pergunta multi-intenção
    # ------------------------------------------------------------------
    def test_scenario_2_multi_intent(self):
        """'Grávida pode tomar dipirona junto com ibuprofeno?' → PREGNANCY + INTERACTION."""
        res = self.retriever.retrieve(
            "Grávida pode tomar dipirona junto com ibuprofeno?",
            medication="Dipirona",
            debug=True,
        )

        qu = res.query_understanding
        self.assertIsNotNone(qu)

        detected_intents = {c.intent for c in qu.intent_candidates}

        # Deve detectar PREGNANCY_LACTATION e INTERACTION
        self.assertIn(QueryIntent.PREGNANCY_LACTATION, detected_intents)
        self.assertIn(QueryIntent.INTERACTION, detected_intents)

        # Estratégia deve ser graph_hybrid_restricted (múltiplas intenções)
        self.assertEqual(qu.retrieval_plan.strategy, "graph_hybrid_restricted")

    # ------------------------------------------------------------------
    # Cenário 3: Pergunta vaga
    # ------------------------------------------------------------------
    def test_scenario_3_vague_question(self):
        """'Esse remédio é perigoso?' → baixa confiança, graph_broad_safety."""
        res = self.retriever.retrieve(
            "Esse remédio é perigoso?",
            medication="Dipirona",
            debug=True,
        )

        qu = res.query_understanding
        self.assertIsNotNone(qu)

        # Estratégia deve ser graph_broad_safety (baixa confiança)
        self.assertEqual(qu.retrieval_plan.strategy, "graph_broad_safety")

        # Seções críticas devem estar no plano
        plan_section_values = {s.value for s in qu.retrieval_plan.target_sections}
        # Deve incluir seções de segurança
        self.assertTrue(
            plan_section_values & {"contraindication", "warning_precaution", "adverse_reaction"},
            f"Seções de segurança esperadas, mas encontradas: {plan_section_values}",
        )

    # ------------------------------------------------------------------
    # Cenário 4: Pergunta sobre posologia
    # ------------------------------------------------------------------
    def test_scenario_4_dosage(self):
        """'Como devo tomar esse medicamento?' → DOSAGE."""
        res = self.retriever.retrieve(
            "Como devo tomar esse medicamento?",
            medication="Dipirona",
            debug=True,
        )

        self.assertEqual(res.intent, "dosage")

        qu = res.query_understanding
        self.assertIsNotNone(qu)

        top_intent = qu.intent_candidates[0].intent
        self.assertEqual(top_intent, QueryIntent.DOSAGE)

        # Deve ter evidência sobre posologia
        self.assertGreater(len(res.evidence), 0)

    # ------------------------------------------------------------------
    # Cenário 5: Pergunta sobre reação adversa
    # ------------------------------------------------------------------
    def test_scenario_5_adverse_reaction(self):
        """'Esse remédio dá sono?' → ADVERSE_REACTION."""
        res = self.retriever.retrieve(
            "Esse remédio dá sono?",
            medication="Dipirona",
            debug=True,
        )

        self.assertEqual(res.intent, "adverse_reaction")

        qu = res.query_understanding
        self.assertIsNotNone(qu)

        top_intent = qu.intent_candidates[0].intent
        self.assertEqual(top_intent, QueryIntent.ADVERSE_REACTION)

    # ------------------------------------------------------------------
    # Cenário 6: Pergunta sobre condição clínica (hepato/renal)
    # ------------------------------------------------------------------
    def test_scenario_6_renal_hepatic(self):
        """'Quem tem problema no fígado pode tomar?' → RENAL_HEPATIC e/ou WARNING/CONTRAINDICATION."""
        res = self.retriever.retrieve(
            "Quem tem problema no fígado pode tomar?",
            medication="Dipirona",
            debug=True,
        )

        qu = res.query_understanding
        self.assertIsNotNone(qu)

        detected_intents = {c.intent for c in qu.intent_candidates}

        # Deve detectar RENAL_HEPATIC
        self.assertIn(QueryIntent.RENAL_HEPATIC, detected_intents)

        # Seções no plano devem incluir warning_precaution e/ou contraindication
        plan_section_values = {s.value for s in qu.retrieval_plan.target_sections}
        safety_overlap = plan_section_values & {"warning_precaution", "contraindication"}
        self.assertTrue(
            safety_overlap,
            f"Esperava seções de segurança, mas encontrou: {plan_section_values}",
        )

        # Deve ter evidência
        self.assertGreater(len(res.evidence), 0)

    # ------------------------------------------------------------------
    # Testes de confiança
    # ------------------------------------------------------------------
    def test_confidence_structure(self):
        """Testa que confidence contém as 3 camadas."""
        res = self.retriever.retrieve(
            "Dipirona interage com varfarina?",
            medication="Dipirona",
        )
        self.assertIn("intent_confidence", res.confidence)
        self.assertIn("retrieval_confidence", res.confidence)
        self.assertIn("answer_confidence", res.confidence)

        # Todos devem estar entre 0 e 1
        for key in ("intent_confidence", "retrieval_confidence", "answer_confidence"):
            value = res.confidence[key]
            self.assertGreaterEqual(value, 0.0)
            self.assertLessEqual(value, 1.0)

    def test_query_understanding_audit(self):
        """Testa que QueryUnderstanding é preenchido e auditável."""
        res = self.retriever.retrieve(
            "Grávida pode tomar dipirona junto com ibuprofeno?",
            medication="Dipirona",
        )
        qu = res.query_understanding
        self.assertIsNotNone(qu)
        self.assertIsInstance(qu, QueryUnderstanding)
        self.assertEqual(qu.question, "Grávida pode tomar dipirona junto com ibuprofeno?")
        self.assertGreater(len(qu.intent_candidates), 0)
        self.assertGreater(len(qu.section_candidates), 0)
        self.assertIsInstance(qu.retrieval_plan, RetrievalPlan)
        self.assertGreaterEqual(qu.intent_confidence, 0.0)
        self.assertGreaterEqual(qu.entity_confidence, 0.0)


if __name__ == "__main__":
    unittest.main()
