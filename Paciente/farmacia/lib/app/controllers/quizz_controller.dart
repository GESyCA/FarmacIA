import 'package:farmacia/app/data/models/quizz_question_model.dart';
import 'package:farmacia/app/data/models/quizz_question_score_model.dart';
import 'package:farmacia/app/data/repositories/quizz_repository.dart';
import 'package:get/get.dart';

class QuizzController extends GetxController {
  final QuizzRepository repository;

  QuizzController(this.repository);

  final RxList<QuizzQuestionModel> _questions = <QuizzQuestionModel>[].obs;

  List<QuizzQuestionModel> get questions => _questions;

  final RxList<QuizzQuestionScoreModel> _scores = <QuizzQuestionScoreModel>[].obs;
  List<QuizzQuestionScoreModel> get scores => _scores;

  final RxInt currentQuestionIndex = 0.obs;

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
      (index) => QuizzQuestionScoreModel(
        questionId: _questions[index].id,
        score: 0,
      ),
    );
  }
}
