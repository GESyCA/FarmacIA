import 'dart:convert';

FeedbackModel feedbackModelFromJson(String str) => FeedbackModel.fromJson(json.decode(str));

String feedbackModelToJson(FeedbackModel data) => json.encode(data.toJson());

class FeedbackModel {
    final int messageId;
    final int score;
    final String comment;

    FeedbackModel({
        required this.messageId,
        required this.score,
        required this.comment,
    });

    FeedbackModel copyWith({
        int? messageId,
        int? score,
        String? comment,
    }) => 
        FeedbackModel(
            messageId: messageId ?? this.messageId,
            score: score ?? this.score,
            comment: comment ?? this.comment,
        );

    factory FeedbackModel.fromJson(Map<String, dynamic> json) => FeedbackModel(
        messageId: json["message_id"],
        score: json["score"],
        comment: json["comment"],
    );

    Map<String, dynamic> toJson() => {
        "message_id": messageId,
        "score": score,
        "comment": comment,
    };
}
