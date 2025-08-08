import 'dart:convert';

class Answer {
    final String resposta;
    final String conversationId;

    Answer({
        required this.resposta,
        required this.conversationId,
    });

    factory Answer.fromRawJson(String str) => Answer.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory Answer.fromJson(Map<String, dynamic> json) => Answer(
        resposta: json["resposta"],
        conversationId: json["conversation_id"]
    );

    Map<String, dynamic> toJson() => {
        "resposta": resposta,
        "conversation_id": conversationId,
    };
}
