import 'package:farmacia/app/ui/widgets/quizz_card.dart';
import 'package:flutter/material.dart';

class QuizzPage extends StatefulWidget {
  const QuizzPage({super.key});

  @override
  State<QuizzPage> createState() => _QuizzPageState();
}

class _QuizzPageState extends State<QuizzPage> {
  int currentIndex = 0;

  final List<Map<String, dynamic>> questions = [
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
      "question": "Durante as férias, ou fins de semana, às vezes esqueço de tomar a medicação",
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

  void nextQuestion() {
    if (currentIndex < questions.length - 1) {
      setState(() => currentIndex++);
    }
  }

  void previousQuestion() {
    if (currentIndex > 0) {
      setState(() => currentIndex--);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: AppBar(
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        centerTitle: true,
        title: const Text("Quiz"),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () {
              Navigator.pushNamed(context, '/login');
            },
          ),
        ],
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            QuizCard(
              question: questions[currentIndex]["question"] ?? "",
              imageAsset: questions[currentIndex]["image"] ?? "",
              questionNumber: currentIndex + 1,
              totalQuestions: questions.length,
              onNext: nextQuestion,
              onPrevious: previousQuestion,
              selectedRating: questions[currentIndex]["alternativa"] ?? 0,
              onChanged: (val) {
                setState(() {
                  questions[currentIndex]["alternativa"] = val;
                });
              },
            )
          ],
        ),
      ),
    );
  }
}
