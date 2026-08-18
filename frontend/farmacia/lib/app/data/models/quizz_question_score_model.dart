import 'dart:convert';

class QuizzQuestionScoreModel {
    final int questionId;
    final int score;

    QuizzQuestionScoreModel({
        required this.questionId,
        required this.score,
    });

    QuizzQuestionScoreModel copyWith({
        int? questionId,
        int? score,
    }) => 
        QuizzQuestionScoreModel(
            questionId: questionId ?? this.questionId,
            score: score ?? this.score,
        );

    factory QuizzQuestionScoreModel.fromRawJson(String str) => QuizzQuestionScoreModel.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory QuizzQuestionScoreModel.fromJson(Map<String, dynamic> json) => QuizzQuestionScoreModel(
        questionId: json["question_id"],
        score: json["score"],
    );

    Map<String, dynamic> toJson() => {
        "question_id": questionId,
        "score": score,
    };
}
