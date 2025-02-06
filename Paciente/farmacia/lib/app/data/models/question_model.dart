import 'dart:convert';

class QuestionModel {
    final String nomeRemedio;
    final String pergunta;

    QuestionModel({
        required this.nomeRemedio,
        required this.pergunta,
    });

    factory QuestionModel.fromRawJson(String str) => QuestionModel.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory QuestionModel.fromJson(Map<String, dynamic> json) => QuestionModel(
        nomeRemedio: json["nome_remedio"],
        pergunta: json["pergunta"],
    );

    Map<String, dynamic> toJson() => {
        "nome_remedio": nomeRemedio,
        "pergunta": pergunta,
    };
}
