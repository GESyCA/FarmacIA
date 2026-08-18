import 'dart:convert';

class QuestionModel {
    final String nomeRemedio;
    final String pergunta;
    String? conversationId;

    QuestionModel({
        required this.nomeRemedio,
        required this.pergunta,
        this.conversationId,
    });

    factory QuestionModel.fromRawJson(String str) => QuestionModel.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory QuestionModel.fromJson(Map<String, dynamic> json) => QuestionModel(
        nomeRemedio: json["nome_remedio"],
        pergunta: json["pergunta"],
        conversationId: json["conversation_id"],
    );

    Map<String, dynamic> toJson() => {
        "nome_remedio": nomeRemedio,
        "pergunta": pergunta,
        "conversation_id": conversationId,
    };
}
