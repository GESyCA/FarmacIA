import 'package:farmacia/app/controllers/quizz_controller.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class SendQuizzDialog extends GetView<QuizzController> {
  const SendQuizzDialog({super.key});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(height: 24),
          CircleAvatar(
            backgroundColor: Colors.green[100],
            radius: 35,
            child: Icon(
              Icons.check,
              color: Colors.green[700],
              size: 40,
            ),
          ),
          SizedBox(
            height: 12,
          ),
          Text(
            "Parabéns, você concluiu o quizz!",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(
            height: 16,
          ),
          Container(
            width: double.infinity,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.only(
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: Obx( () {
                return Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    TextButton.icon(
                      onPressed:
                          controller.isLoading
                              ? null
                              : () {
                                Get.back();
                                controller.previousQuestion();
                              },
                      label: Text("Cancelar"),
                      style: TextButton.styleFrom(
                        foregroundColor: Color(0xFFB9160C),
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: BorderSide(color: Color(0xFFB9160C)),
                        ),
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: controller.isLoading
                              ? null
                              : () {
                                controller.submitAnswers();
                              },
                      label:
                          controller.isLoading
                              ? SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(color: Colors.white),
                              )
                              : Text("Enviar"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color(0xFFB9160C),
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ],
                );
              }
            ),
          )
        ],
      ),
    );
  }
}