import 'package:farmacia/app/data/repositories/quizz_repository.dart';
import 'package:get/get.dart';

class QuizzController extends GetxController {
  final QuizzRepository repository;

  QuizzController(this.repository);

  final RxList questions = [].obs;

  final RxInt currentQuestionIndex = 0.obs;

  void nextQuestion() {
    if (currentQuestionIndex.value < questions.length - 1) {
      currentQuestionIndex.value++;
    }
  }

  void previousQuestion() {
    if (currentQuestionIndex.value > 0) {
      currentQuestionIndex.value--;
    }
  }

  @override
  void onInit() {
    super.onInit();
    loadQuestions();
  }

  void loadQuestions() async {
    questions.value = [
      {
        "question":
            "Evito comportamentos que podem prejudicar a minha saúde (ex. tabaco, álcool)",
        "image": "assets/no_alcohol.png",
        "alternativa": 0,
      },
      {
        "question": "Não gosto de tomar medicamentos todos os dias",
        "image": "assets/quiz/calendar.png",
        "alternativa": 0,
      },
      {
        "question":
            "Durante as férias, ou fins de semana, às vezes esqueço de tomar a medicação",
        "image": "assets/quiz/vacation.png",
        "alternativa": 0,
      },
      {
        "question": "Sinto-me melhor ao tomar a medicação todos os dias",
        "image": "assets/quiz/health.png",
        "alternativa": 0,
      },
      {
        "question": "Às vezes não tenho certeza se tomei os meus comprimidos",
        "image": "assets/quiz/help.png",
        "alternativa": 0,
      },
    ];
  }
}
