import 'package:farmacia/app/controllers/quizz_controller.dart';
import 'package:farmacia/app/ui/widgets/custom_app_bar.dart';
import 'package:farmacia/app/ui/widgets/quizz_card.dart';
import 'package:flutter/material.dart';
import 'package:get/state_manager.dart';

class QuizzPage extends GetView<QuizzController> {
  QuizzPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.grey[200],
      appBar: CustomAppBar(title: 'Quizz'),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Obx(() {
              int currentIndex = controller.currentQuestionIndex.value;
              return QuizCard(
                question: controller.questions[currentIndex]["question"] ?? "",
                imageAsset: controller.questions[currentIndex]["image"] ?? "",
                questionNumber: currentIndex + 1,
                totalQuestions: controller.questions.length,
                onNext: controller.nextQuestion,
                onPrevious: controller.previousQuestion,
                selectedRating:
                    controller.questions[currentIndex]["alternativa"] ?? 0,
                onChanged: (val) {
                  controller.questions[currentIndex]["alternativa"] = val;
                },
              );
            })
          ],
        ),
      ),
    );
  }
}

class QuizzView extends StatefulWidget {
  final List<Map<String, dynamic>> questions;

  const QuizzView({super.key, required this.questions});

  @override
  State<QuizzView> createState() => _QuizzViewState();
}

class _QuizzViewState extends State<QuizzView> {
  int currentIndex = 0;

  void nextQuestion() {
    if (currentIndex < widget.questions.length - 1) {
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
    final questions = widget.questions;
    return Column(
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
        ),
      ],
    );
  }
}
