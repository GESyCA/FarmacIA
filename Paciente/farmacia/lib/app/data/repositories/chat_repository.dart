import 'dart:async';

import 'package:farmacia/app/data/http/http_client.dart';
import 'package:farmacia/app/data/models/answer_model.dart';
import 'package:farmacia/app/data/models/question_model.dart';

class ChatRepository {
  final IHttpClient httpClient;

  ChatRepository({required this.httpClient});

  Future<Answer> sendMessage(QuestionModel question) async {
    try {
      final response = await httpClient
          .post(
            '/perguntar',
            body: question.toJson(),
          )
          .timeout(const Duration(seconds: 5));
      if (response.statusCode == 200) {
        return Answer.fromJson(response.body as Map<String, dynamic>);
      } else {
        return Answer(resposta: 'Desculpe, não entendi a pergunta');
      }
    } on TimeoutException {
      return Answer(resposta: 'Desculpe, tempo foi exedido');
    } catch (e) {
      return Answer(resposta: 'Desculpe, não entendi a pergunta');
    }
  }
}
