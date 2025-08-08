import 'package:farmacia/app/data/models/question_model.dart';
import 'package:farmacia/app/data/repositories/chat_repository.dart';
import 'package:farmacia/app/ui/widgets/robot_avatar.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ChatController extends GetxController {
  final ChatRepository repository;

  ChatController(this.repository);

  final TextEditingController textController = TextEditingController();

  final List<Widget> _messages = <Widget>[].obs;
  List<Widget> get messages => _messages;

  final RxBool _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final RxBool _showPrompts = true.obs;
  bool get showPrompts => _showPrompts.value;

  late final String medicineName;
  late final String userId;

  @override
  void onInit() {
    super.onInit();
    medicineName = Get.arguments['medicine'] ?? 'Paracetamol';
    userId = Get.arguments['userId'] ?? '';
  }

  void togglePrompts() {
    _showPrompts.value = !_showPrompts.value;
  }

  void handleSubmitted(String text) async {
    if (text.isEmpty) return;

    textController.clear();
    _showPrompts.value = false;

    messages.insert(0, _buildUserMessage(text));
    final loading = _buildLoadingMessage();
    messages.insert(0, loading);

    final answer = await repository.sendMessage(
      QuestionModel(nomeRemedio: medicineName, pergunta: text),
    );

    messages.remove(loading);
    messages.insert(0, _buildLLMResponse(answer.resposta));
  }

  void sendPrompt(String prompt) {
    handleSubmitted(prompt);
  }

  Widget _buildUserMessage(String text) {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 4.0),
      alignment: Alignment.centerRight,
      child: Container(
        padding: EdgeInsets.all(12.0),
        decoration: BoxDecoration(
          color: Colors.red,
          borderRadius: BorderRadius.circular(8.0),
        ),
        child: Text(
          text,
          style: TextStyle(fontSize: 14.0, color: Colors.white),
        ),
      ),
    );
  }

  Widget _buildLLMResponse(String text) {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 4.0),
      alignment: Alignment.centerLeft,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RobotAvatar(),
          SizedBox(width: 8.0),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Text(text, style: TextStyle(fontSize: 14.0)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingMessage() {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 4.0),
      alignment: Alignment.centerLeft,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RobotAvatar(),
          SizedBox(width: 8.0),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Row(children: [_buildTypingIndicator()]),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypingIndicator() {
    return SizedBox(
      height: 10,
      width: 24,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(3, (index) {
          return AnimatedContainer(
            duration: Duration(milliseconds: 500),
            curve: Curves.easeInOut,
            height: 6,
            width: 6,
            margin: EdgeInsets.symmetric(horizontal: 1),
            decoration: BoxDecoration(
              color: Colors.grey,
              shape: BoxShape.circle,
            ),
          );
        }),
      ),
    );
  }
}
