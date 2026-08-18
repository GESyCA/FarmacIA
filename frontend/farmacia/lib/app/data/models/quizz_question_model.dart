import 'dart:convert';

class QuizzQuestionModel {
    final int id;
    final int number;
    final String question;

    QuizzQuestionModel({
        required this.id,
        required this.number,
        required this.question,
    });

    QuizzQuestionModel copyWith({
        int? id,
        int? number,
        String? question,
    }) => 
        QuizzQuestionModel(
            id: id ?? this.id,
            number: number ?? this.number,
            question: question ?? this.question,
        );

    factory QuizzQuestionModel.fromRawJson(String str) => QuizzQuestionModel.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory QuizzQuestionModel.fromJson(Map<String, dynamic> json) => QuizzQuestionModel(
        id: json["id"],
        number: json["number"],
        question: json["question"],
    );

    Map<String, dynamic> toJson() => {
        "id": id,
        "number": number,
        "question": question,
    };
}
