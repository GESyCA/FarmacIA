from flask import Blueprint, jsonify, request
from models import MauqQuestions

bp = Blueprint('mauq', __name__)

@bp.route('/questoes', methods=['GET'])
def get_mauq_questions():

    try:
        questions_from_db = MauqQuestions.query.all()

        formatted_questions = []
        for q in questions_from_db:
            formatted_questions.append({
                'id': q.id,
                'number': q.number,
                'question': q.question
            })

        return jsonify(formatted_questions)

    except Exception as e:
        print(f"Erro ao buscar questões: {e}")
        return jsonify({"error": "Ocorreu um erro interno ao buscar as questões."}), 500


@bp.route('/responder', methods=['POST'])
def process_mauq_answers():
    answers_data = request.json
    
    if not isinstance(answers_data, list) or not answers_data:
        return jsonify({"error": "O corpo do pedido deve ser uma lista de respostas e não pode estar vazio."}), 400

    all_questions_db = MauqQuestions.query.all()
    questions_map = {q.id: q for q in all_questions_db}
    processed_scores = []

    for answer in answers_data:
        question_id = answer.get('question_id')
        score = answer.get('score')

        if question_id is None or score is None or not (isinstance(score, int) and 1 <= score <= 7):
            return jsonify({"error": f"Resposta inválida ou faltando para a questão {question_id or 'desconhecida'}."}), 400

        question = questions_map.get(question_id)
        if not question:
            return jsonify({"error": f"Questão com id {question_id} não encontrada."}), 404
        
        adjusted_score = 8 - score if question.inverted else score
        processed_scores.append({"score": adjusted_score, "dimension": question.dimension})

    
    scores_por_dimensao = {1: [], 2: [], 3: [], 4: []}
    for item in processed_scores:
        dim = item['dimension']
        if dim in scores_por_dimensao:
            scores_por_dimensao[dim].append(item['score'])

    resultado_dimensoes = {}
    soma_total_scores = 0

    for dim, scores in scores_por_dimensao.items():
        soma_dimensao = sum(scores)
        soma_total_scores += soma_dimensao
        
        resultado_dimensoes[dim] = round((soma_dimensao / 28) * 100, 2)

    score_geral = round((soma_total_scores / 112) * 100, 2)

    return jsonify({
        "score_geral_percentual": score_geral,
        "scores_dimensoes_percentual": resultado_dimensoes
    })