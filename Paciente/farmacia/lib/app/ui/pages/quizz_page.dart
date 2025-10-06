import 'package:farmacia/app/controllers/quizz_controller.dart';
import 'package:farmacia/app/ui/modal/send_quizz_dialog.dart';
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

              if (controller.isLoadingQuestions) {
                return CircularProgressIndicator();
              }

              int currentIndex = controller.currentQuestionIndex.value;
                if (currentIndex >= controller.questions.length) {
                Future.microtask(() {
                  showDialog(
                  context: context,
                  barrierDismissible: false,
                  builder: (context) => SendQuizzDialog()
                  );
                });
                return SizedBox.shrink();
                }
              return QuizCard(
                question: controller.questions[currentIndex].question,
                imageAsset: "assets/quiz/health.png",
                questionNumber: currentIndex + 1,
                totalQuestions: controller.questions.length,
                onNext: controller.nextQuestion,
                onPrevious: controller.previousQuestion,
                selectedRating: controller.scores[currentIndex].score,
                onChanged: (val) {
                  controller.scores[currentIndex] =
                    controller.scores[currentIndex].copyWith(score: val);
                },
              );
            })
          ],
        ),
      ),
    );
  }
}

