import 'package:hive/hive.dart';
import 'dart:convert';

part 'statistics_model.g.dart';

@HiveType(typeId: 2)
class StatisticsModel {
    @HiveField(1)
    final double scoreGeralPercentual;
    @HiveField(2)
    final Map<String, double> scoresDimensoesPercentual;

    StatisticsModel({
        required this.scoreGeralPercentual,
        required this.scoresDimensoesPercentual,
    });

    StatisticsModel copyWith({
        double? scoreGeralPercentual,
        Map<String, double>? scoresDimensoesPercentual,
    }) => 
        StatisticsModel(
            scoreGeralPercentual: scoreGeralPercentual ?? this.scoreGeralPercentual,
            scoresDimensoesPercentual: scoresDimensoesPercentual ?? this.scoresDimensoesPercentual,
        );

    factory StatisticsModel.fromRawJson(String str) => StatisticsModel.fromJson(json.decode(str));

    String toRawJson() => json.encode(toJson());

    factory StatisticsModel.fromJson(Map<String, dynamic> json) => StatisticsModel(
        scoreGeralPercentual: json["score_geral_percentual"]?.toDouble(),
        scoresDimensoesPercentual: Map.from(json["scores_dimensoes_percentual"]).map((k, v) => MapEntry<String, double>(k, v?.toDouble())),
    );

    Map<String, dynamic> toJson() => {
        "score_geral_percentual": scoreGeralPercentual,
        "scores_dimensoes_percentual": Map.from(scoresDimensoesPercentual).map((k, v) => MapEntry<String, dynamic>(k, v)),
    };
}
