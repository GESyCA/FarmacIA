from flask import Blueprint, request, jsonify
from services.bula_service import perguntar_sobre_bula
from services.bula_service import topicos_bula
from models import db, Conversation, Message, Feedback

bp = Blueprint('bula', __name__)

@bp.route('/', methods=['GET'])
def index():
    return jsonify({"message": "ola"})

@bp.route('/perguntar', methods=['POST'])
def perguntar_sobre_bula_route():
    data = request.json
    nome_remedio = data.get('nome_remedio')
    pergunta = data.get('pergunta')
    conversation_id = data.get('conversation_id')

    if not nome_remedio or not pergunta:
        return jsonify({"error": "Nome do remédio e pergunta são obrigatórios"}), 400

    conversa_atual = None
    
    # Se um ID de conversa foi fornecido
    if conversation_id:
        conversa_atual = Conversation.query.get(conversation_id)
        if not conversa_atual:
            return jsonify({"error": "ID de conversa inválido"}), 404

    if not conversa_atual:
        conversa_atual = Conversation(nome_remedio=nome_remedio)
        db.session.add(conversa_atual)

        db.session.commit()

    # Salva a mensagem do usuário no banco
    mensagem_usuario = Message(
        conversation_id=conversa_atual.id,
        role='user',
        content=pergunta
    )
    db.session.add(mensagem_usuario)
    db.session.commit()

    # Busca todas as mensagens da conversa atual, ordenadas por data
    mensagens_anteriores = Message.query.filter_by(conversation_id=conversa_atual.id).order_by(Message.created_at).all()
    
    historico_formatado = []
    for msg in mensagens_anteriores:
        historico_formatado.append({"role": msg.role, "content": msg.content})

    resposta_llm = perguntar_sobre_bula(
        nome_remedio=conversa_atual.nome_remedio,
        pergunta=pergunta,
        historico_conversa=historico_formatado
    )

    # Salve a resposta do LLM no banco
    mensagem_llm = Message(
        conversation_id=conversa_atual.id,
        role='assistant',
        content=resposta_llm
    )
    db.session.add(mensagem_llm)
    db.session.commit()

    assistant_message_id = mensagem_llm.id

    # Retorna a resposta junto com ids
    return jsonify({
        "resposta": resposta_llm,
        "conversation_id": conversa_atual.id,
        "assistant_message_id": assistant_message_id
    })


@bp.route('/feedback', methods=['POST'])
def registrar_feedback_route():
    data = request.json
    message_id = data.get('message_id')
    score = data.get('score')
    comment = data.get('comment')

    if not message_id or score is None:
        return jsonify({"error": "message_id e score são obrigatórios"}), 400

    # Valida se a mensagem existe e pertence ao assistente
    message = Message.query.get(message_id)
    if not message:
        return jsonify({"error": "Mensagem não encontrada"}), 404
    if message.role != 'assistant':
        return jsonify({"error": "O feedback só pode ser dado para respostas do assistente"}), 400
        
    # Impede que o mesmo feedback seja enviado duas vezes
    if message.feedback:
        return jsonify({"error": "O feedback para esta mensagem já foi registrado"}), 409

    # Cria e salva o novo registro de feedback
    novo_feedback = Feedback(
        message_id=message_id,
        score=score,
        comment=comment
    )
    db.session.add(novo_feedback)
    db.session.commit()

    return jsonify({"success": True, "message": "Feedback registrado com sucesso!"}), 201

@bp.route('/topicos', methods=['POST'])
def topicos_bula_route():
    data = request.json
    nome_remedio = data.get('nome_remedio')
    pergunta = data.get('pergunta')

    if not nome_remedio or not pergunta:
        return jsonify({"error": "Nome do remédio e pergunta são obrigatórios"}), 400
    
    resposta = topicos_bula(nome_remedio, pergunta)
    return jsonify({"topicos": resposta})