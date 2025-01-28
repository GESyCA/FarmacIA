from flask import Blueprint, request, jsonify
from app.services.bula_service import buscar_bula, perguntar_sobre_bula

bp = Blueprint('bula', __name__)

@bp.route('/buscar_bula', methods=['POST'])
def buscar_bula_route():
    data = request.json
    nome_remedio = data.get('nome_remedio')
    if not nome_remedio:
        return jsonify({"error": "Nome do remédio é obrigatório"}), 400
    
    resultado = buscar_bula(nome_remedio)
    return jsonify(resultado)

@bp.route('/perguntar', methods=['POST'])
def perguntar_sobre_bula_route():
    data = request.json
    nome_remedio = data.get('nome_remedio')
    pergunta = data.get('pergunta')
    if not nome_remedio or not pergunta:
        return jsonify({"error": "Nome do remédio e pergunta são obrigatórios"}), 400
    
    resposta = perguntar_sobre_bula(nome_remedio, pergunta)
    return jsonify({"resposta": resposta})