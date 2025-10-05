import 'package:farmacia/app/data/http/http_client.dart';
import 'package:farmacia/app/data/models/hive/statistics_model.dart';
import 'package:farmacia/app/data/models/quizz_question_model.dart';
import 'package:farmacia/app/data/models/quizz_question_score_model.dart';

class QuizzRepository {
  final IHttpClient httpClient;

  QuizzRepository({required this.httpClient});

  Future<List<QuizzQuestionModel>> fetchQuestions() async {
    try {
      final response = await httpClient.get('questoes');
      if (response.statusCode == 200) {
        final List<dynamic> data = response.body as List;
        return data
            .map((item) => QuizzQuestionModel.fromJson(item))
            .toList();
      } else {
        print("Erro: ${response.statusCode}");
        return [];
      }
    } catch (e) {
      print("Erro: $e");
      return [];
    }
  }

  Future<StatisticsModel> submitQuizzAnswers(QuizzQuestionScoreModel scores) async {
    try {
      final response = await httpClient.post(
        'respostas',
        body: scores.toJson(),
      );
      if (response.statusCode == 200) {
        return StatisticsModel.fromJson(response.body as Map<String, dynamic>);
      } else {
        throw Exception('Failed to submit answers: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Failed to submit answers: $e');
    }
  }
}