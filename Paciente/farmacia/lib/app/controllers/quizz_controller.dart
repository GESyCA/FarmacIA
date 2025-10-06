import 'package:farmacia/app/data/models/quizz_question_model.dart';
import 'package:farmacia/app/data/models/quizz_question_score_model.dart';
import 'package:farmacia/app/data/repositories/quizz_repository.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class QuizzController extends GetxController {
  final QuizzRepository repository;

  QuizzController(this.repository);

  final RxList<QuizzQuestionModel> _questions = <QuizzQuestionModel>[].obs;

  List<QuizzQuestionModel> get questions => _questions;

  final RxList<QuizzQuestionScoreModel> _scores =
      <QuizzQuestionScoreModel>[].obs;
  List<QuizzQuestionScoreModel> get scores => _scores;

  final RxInt currentQuestionIndex = 0.obs;

  final RxBool _isLoading = false.obs;
  bool get isLoading => _isLoading.value;
  set isLoading(bool value) => _isLoading.value = value;

  void nextQuestion() {
    if (currentQuestionIndex.value < _questions.length - 1) {
      currentQuestionIndex.value++;
    }
  }

  void previousQuestion() {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--;
    }
  }

  @override
  void onInit() async {
    super.onInit();
    await loadQuestions();
  }

  Future<void> loadQuestions() async {
    _questions.value = await repository.fetchQuestions();
    _scores.value = List.generate(
      _questions.length,
      (index) =>
          QuizzQuestionScoreModel(questionId: _questions[index].id, score: 0),
    );
  }

  Future<void> submitAnswers() async {
    isLoading = true;
    try {
      final statistics = await repository.submitQuizzAnswers(_scores);
      // Aqui você pode fazer algo com as estatísticas retornadas, como armazená-las ou exibi-las
      print('Pontuação geral: ${statistics.scoreGeralPercentual}');
      Get.snackbar(
        'Sucesso',
        'Respostas enviadas com sucesso! Sua pontuação: ${statistics.scoreGeralPercentual}%',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green.withOpacity(0.8),
        colorText: Colors.white,
      );
    } catch (e) {
      print('Erro ao enviar respostas: $e');
      Get.snackbar(
        'Erro',
        'Falha ao enviar respostas. Tente novamente mais tarde.',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
      );
    } finally {
      isLoading = false;
    }
  }
}
