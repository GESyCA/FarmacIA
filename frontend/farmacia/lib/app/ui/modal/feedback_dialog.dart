import 'package:farmacia/app/controllers/chat_controller.dart';
import 'package:farmacia/app/data/models/feedback_model.dart';
import 'package:flutter/material.dart';
import 'package:flutter_rating_bar/flutter_rating_bar.dart';
import 'package:get/get.dart';

class FeedbackDialog extends GetView<ChatController> {
  final int messageId;
  const FeedbackDialog({super.key, required this.messageId});

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(height: 40),
          Text(
            "Qual nota você dá para a resposta?",
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
          ),
          SizedBox(height: 12),
          RatingBar.builder(
            initialRating: controller.rating,
            minRating: 0,
            direction: Axis.horizontal,
            allowHalfRating: false,
            itemCount: 5,
            itemSize: 40.0,
            itemPadding: EdgeInsets.symmetric(horizontal: 4.0),
            unratedColor: Colors.grey[300],
            onRatingUpdate: (rating) {
              controller.setRating(rating);
            },
            itemBuilder: (context, _) => Icon(Icons.star, color: Colors.amber),
          ),
          SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16.0),
            child: TextField(
              controller: controller.feedbackController,
              decoration: InputDecoration(
                labelText: "Deixe um comentário (opcional)",
              ),
            ),
          ),
          SizedBox(height: 32),
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
                          controller.isFeedbackSent
                              ? null
                              : () {
                                Get.back();
                                controller.feedbackController.clear();
                                controller.setRating(0);
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
                      onPressed:
                          controller.isFeedbackSent
                              ? null
                              : () {
                                controller.sendFeedback(
                                  FeedbackModel(
                                    messageId: messageId,
                                    score: controller.rating.toInt(),
                                    comment: controller.feedbackController.text,
                                  ),
                                );
                              },
                      label:
                          controller.isFeedbackSent
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
          ),
        ],
      ),
    );
  }
}
