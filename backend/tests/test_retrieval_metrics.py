import sys
import os
import unittest

# Adiciona o diretório raiz e o diretório app ao sys.path
# Para que as importações funcionem tanto se rodar de Paciente/app/ quanto do workspace root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from rag.evaluation.retrieval_metrics import (
    extract_chunk_id,
    get_gold_chunk_ids,
    recall_at_k,
    evidence_set_recall_at_k,
    mrr_at_k,
    ndcg_at_k,
    evaluate_retrieval
)

class TestRetrievalMetrics(unittest.TestCase):
    """Testes unitários para as métricas de recuperação RAG."""

    def test_chunk_id_normalization(self):
        """Testa a extração e normalização do ID do chunk de diferentes formatos."""
        # 1. chunk_id
        self.assertEqual(extract_chunk_id({"chunk_id": "c1"}), "c1")
        # 2. id
        self.assertEqual(extract_chunk_id({"id": "c2"}), "c2")
        # 3. metadata.chunk_id
        self.assertEqual(extract_chunk_id({"metadata": {"chunk_id": "c3"}}), "c3")
        # 4. metadata.id
        self.assertEqual(extract_chunk_id({"metadata": {"id": "c4"}}), "c4")
        # String direta
        self.assertEqual(extract_chunk_id("c5"), "c5")
        # Casos nulos ou inválidos
        self.assertIsNone(extract_chunk_id(None))
        self.assertIsNone(extract_chunk_id({}))
        self.assertIsNone(extract_chunk_id(123))

    def test_perfect_hit(self):
        """Testa o cenário onde todas as evidências são recuperadas no topo do ranking."""
        gold = {"c1", "c2"}
        retrieved = [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}]
        
        self.assertEqual(recall_at_k(retrieved, gold, k=2), 1.0)
        self.assertEqual(recall_at_k(retrieved, gold, k=1), 0.5)
        
        mrr = mrr_at_k(retrieved, gold, k=2)
        # O primeiro chunk gold ('c1') está na posição 0 (rank 1), logo mrr = 1/1 = 1.0
        self.assertEqual(mrr, 1.0)

    def test_no_hit(self):
        """Testa o cenário onde nenhum chunk relevante é recuperado."""
        gold = {"c1", "c2"}
        retrieved = [{"id": "c3"}, {"id": "c4"}]
        
        self.assertEqual(recall_at_k(retrieved, gold, k=2), 0.0)
        self.assertEqual(mrr_at_k(retrieved, gold, k=2), 0.0)
        
        ev_metrics = evidence_set_recall_at_k(retrieved, gold, k=2)
        self.assertEqual(ev_metrics["evidence_set_recall_at_k"], 0.0)
        self.assertEqual(ev_metrics["evidence_set_hit_at_k"], 0)

    def test_multiple_essential(self):
        """Testa o cálculo com múltiplas evidências essenciais."""
        gold = {"c1", "c2", "c3"}
        retrieved = [{"id": "c4"}, {"id": "c2"}, {"id": "c5"}, {"id": "c3"}]
        
        # Para K=3, recuperados únicos: ['c4', 'c2', 'c5']. Apenas 'c2' está em gold.
        self.assertEqual(recall_at_k(retrieved, gold, k=3), 1/3)
        # Para K=4, recuperados únicos: ['c4', 'c2', 'c5', 'c3']. 'c2' e 'c3' estão em gold.
        self.assertEqual(recall_at_k(retrieved, gold, k=4), 2/3)
        
        # Primeiro gold ('c2') está na posição 1 (rank 2).
        self.assertEqual(mrr_at_k(retrieved, gold, k=3), 0.5)

    def test_duplicates_in_ranking(self):
        """Testa se a presença de duplicatas não infla as métricas."""
        gold = {"c1", "c2"}
        retrieved = [{"id": "c1"}, {"id": "c1"}, {"id": "c2"}]
        
        # Após remover duplicatas: ['c1', 'c2'].
        # Se as duplicatas fossem consideradas, para K=2 teríamos ['c1', 'c1'] (apenas 1 hit).
        # Sem duplicatas, para K=2 temos ['c1', 'c2'] (ambos os hits, recall=1.0).
        self.assertEqual(recall_at_k(retrieved, gold, k=2), 1.0)
        
        # nDCG também não deve ser inflado por duplicatas
        relevance = {"c1": 3, "c2": 3}
        # ndcg deve considerar c1 (rank 1), c2 (rank 2)
        # dcg = (2^3-1)/log2(2) + (2^3-1)/log2(3) = 7/1 + 7/1.58496 = 7 + 4.4165 = 11.4165
        # idcg = dcg = 11.4165
        # ndcg = 1.0
        self.assertAlmostEqual(ndcg_at_k(retrieved, relevance, k=2), 1.0)

    def test_user_example(self):
        """
        Testa o exemplo exato fornecido na especificação do usuário.
        
        Configuração:
          gold essenciais: c1, c2
          gold complementares: c3
          retrieved: c9 (0.9), c1 (0.8), c3 (0.7)
          K = 3
        """
        ground_truth_item = {
            "question_id": "q1",
            "difficulty": "medio",
            "relevant_evidences": [
                {"gold_chunk_id": "c1", "evidence_type": "essential", "relevance_grade": 3},
                {"gold_chunk_id": "c2", "evidence_type": "essential", "relevance_grade": 3},
                {"gold_chunk_id": "c3", "evidence_type": "complementary", "relevance_grade": 2}
            ],
            "retrieval_success_rule_operational_chunks": {
                "essential_gold_chunk_ids": ["c1", "c2"]
            }
        }

        retrieved = [
            {"id": "c9", "score": 0.9},
            {"id": "c1", "score": 0.8},
            {"id": "c3", "score": 0.7}
        ]

        essential_gold_chunk_ids = get_gold_chunk_ids(ground_truth_item, include_complementary=False)
        all_gold_chunk_ids = get_gold_chunk_ids(ground_truth_item, include_complementary=True)

        self.assertEqual(essential_gold_chunk_ids, {"c1", "c2"})
        self.assertEqual(all_gold_chunk_ids, {"c1", "c2", "c3"})

        # Recall@3 apenas com essenciais
        self.assertEqual(recall_at_k(retrieved, essential_gold_chunk_ids, k=3), 0.5) # c1 recuperado de {c1, c2}
        
        # Evidence Set Recall@3
        ev_metrics = evidence_set_recall_at_k(retrieved, essential_gold_chunk_ids, k=3)
        self.assertEqual(ev_metrics["evidence_set_recall_at_k"], 0.5)
        self.assertEqual(ev_metrics["evidence_set_hit_at_k"], 0)

        # MRR@3
        self.assertEqual(mrr_at_k(retrieved, essential_gold_chunk_ids, k=3), 0.5) # c1 está em rank 2

        # nDCG@3
        relevance_by_chunk_id = {"c1": 3, "c2": 3, "c3": 2}
        ndcg_val = ndcg_at_k(retrieved, relevance_by_chunk_id, k=3)
        
        # DCG@3:
        # i=1 (c9, rel=0): (2^0 - 1)/log2(2) = 0
        # i=2 (c1, rel=3): (2^3 - 1)/log2(3) = 7 / 1.58496250072 = 4.416515
        # i=3 (c3, rel=2): (2^2 - 1)/log2(4) = 3 / 2.0 = 1.5
        # DCG@3 = 5.916515
        
        # IDCG@3:
        # Ideal order of relevance grades: 3, 3, 2
        # i=1 (rel=3): (2^3 - 1)/log2(2) = 7 / 1.0 = 7.0
        # i=2 (rel=3): (2^3 - 1)/log2(3) = 7 / 1.58496250072 = 4.416515
        # i=3 (rel=2): (2^2 - 1)/log2(4) = 3 / 2.0 = 1.5
        # IDCG@3 = 12.916515
        
        # nDCG@3 = 5.916515 / 12.916515 = 0.458058
        self.assertAlmostEqual(ndcg_val, 0.458058, places=5)

    def test_out_of_bounds_k(self):
        """Testa se o valor de K maior que a quantidade recuperada é tratado corretamente."""
        gold = {"c1"}
        retrieved = [{"id": "c1"}]
        
        # Deve usar todos os disponíveis
        self.assertEqual(recall_at_k(retrieved, gold, k=10), 1.0)
        self.assertEqual(mrr_at_k(retrieved, gold, k=10), 1.0)

    def test_missing_retrieval_results(self):
        """Testa o comportamento de agregação quando uma pergunta não possui resultados de recuperação."""
        ground_truth = {
            "q1": {
                "question_id": "q1",
                "difficulty": "facil",
                "relevant_evidences": [
                    {"gold_chunk_id": "c1", "evidence_type": "essential", "relevance_grade": 3}
                ],
                "retrieval_success_rule_operational_chunks": {
                    "essential_gold_chunk_ids": ["c1"]
                }
            },
            "q2": {
                "question_id": "q2",
                "difficulty": "facil",
                "relevant_evidences": [
                    {"gold_chunk_id": "c2", "evidence_type": "essential", "relevance_grade": 3}
                ],
                "retrieval_success_rule_operational_chunks": {
                    "essential_gold_chunk_ids": ["c2"]
                }
            }
        }
        
        # Apenas q1 possui resultados, q2 não
        retrieval_results = {
            "q1": [{"id": "c1"}]
        }
        
        report = evaluate_retrieval(ground_truth, retrieval_results, k_values=[1])
        
        # Para q1: recall@1 = 1.0, mrr@1 = 1.0, ndcg@1 = 1.0
        # Para q2: recall@1 = 0.0, mrr@1 = 0.0, ndcg@1 = 0.0 (sem resultados)
        # Geral: recall@1 = 0.5, mrr@1 = 0.5, ndcg@1 = 0.5
        self.assertEqual(report["overall"]["recall@1"], 0.5)
        self.assertEqual(report["overall"]["mrr@1"], 0.5)
        self.assertEqual(report["overall"]["ndcg@1"], 0.5)
        
        # Verifica se q2 está no detalhado por pergunta com valores 0
        q2_detail = next(item for item in report["per_question"] if item["question_id"] == "q2")
        self.assertEqual(q2_detail["recall@1"], 0.0)
        self.assertEqual(q2_detail["mrr@1"], 0.0)
        self.assertEqual(q2_detail["ndcg@1"], 0.0)


if __name__ == "__main__":
    unittest.main()
