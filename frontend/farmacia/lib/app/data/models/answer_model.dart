import 'dart:convert';

class Answer {
  final int? assistantMessageId;
  final String resposta;
  final String conversationId;

    Answer({
      this.assistantMessageId,
      required this.resposta,
      required this.conversationId,
    });

    factory Answer.fromRawJson(String str) => Answer.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory Answer.fromJson(Map<String, dynamic> json) => Answer(
        assistantMessageId: json["assistant_message_id"],
        resposta: json["resposta"],
        conversationId: json["conversation_id"]
    );

    Map<String, dynamic> toJson() => {
        "assistant_message_id": assistantMessageId,
        "resposta": resposta,
        "conversation_id": conversationId,
    };
}
