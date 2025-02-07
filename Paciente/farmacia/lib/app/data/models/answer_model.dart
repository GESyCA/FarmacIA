import 'dart:convert';

class Answer {
    final String resposta;

    Answer({
        required this.resposta,
    });

    factory Answer.fromRawJson(String str) => Answer.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory Answer.fromJson(Map<String, dynamic> json) => Answer(
        resposta: json["resposta"],
    );

    Map<String, dynamic> toJson() => {
        "resposta": resposta,
    };
}
