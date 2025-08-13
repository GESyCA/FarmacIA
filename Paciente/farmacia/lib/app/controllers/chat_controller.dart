import 'package:farmacia/app/data/models/feedback_model.dart';
import 'package:farmacia/app/data/models/hive/conversation_model.dart';
import 'package:farmacia/app/data/models/question_model.dart';
import 'package:farmacia/app/data/repositories/chat_repository.dart';
import 'package:farmacia/app/ui/modal/feedback_dialog.dart';
import 'package:farmacia/app/ui/widgets/robot_avatar.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:hive/hive.dart';

class ChatController extends GetxController {
  final ChatRepository repository;

  ChatController(this.repository);

  final TextEditingController textController = TextEditingController();

  // Substituímos a lista de widgets por um objeto reativo de Conversa
  final Rx<Conversation?> currentConversation = Rx(null);

  final RxBool _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final RxBool _showPrompts = true.obs;
  bool get showPrompts => _showPrompts.value;

  late final String medicineName;
  late final String userId;
  late Box<Conversation> _conversationBox;

  final RxBool _isFeedbackSent = false.obs;
  bool get isFeedbackSent => _isFeedbackSent.value;

  final TextEditingController feedbackController = TextEditingController();

  @override
  void onInit() {
    super.onInit();
    medicineName = Get.arguments['medicine'] ?? 'Paracetamol';
    userId = Get.arguments['userId'] ?? '';
    _conversationBox = Hive.box<Conversation>('conversations');
    _loadConversation();
  }

  void _loadConversation() {
    final key = '${userId}_$medicineName';
    final existingConversation = _conversationBox.get(key);
    if (existingConversation != null) {
      currentConversation.value = existingConversation;
    } else {
      currentConversation.value = Conversation(
        medicineName: medicineName,
        userId: userId,
        messages: [],
      );
    }
  }

  void togglePrompts() {
    _showPrompts.value = !_showPrompts.value;
  }

  void handleSubmitted(String text) async {
    if (text.isEmpty || _isLoading.value) return;

    _isLoading.value = true;
    _showPrompts.value = false;
    final userMessage = ChatMessage(
      text: text,
      isUserMessage: true,
      timestamp: DateTime.now(),
    );
    currentConversation.value?.messages.add(userMessage);
    currentConversation.update((val) {}); // Força a atualização da UI
    textController.clear();

    final answer = await repository.sendMessage(
      QuestionModel(
        nomeRemedio: medicineName,
        pergunta: text,
        conversationId: currentConversation.value?.conversationId,
      ),
    );

    // Salva o ID da conversa retornado pela API
    if (currentConversation.value!.conversationId == null &&
        answer.conversationId != "") {
      currentConversation.value!.conversationId = answer.conversationId;
    }

    final botMessage = ChatMessage(
      text: answer.resposta,
      isUserMessage: false,
      timestamp: DateTime.now(),
      messageId: answer.assistantMessageId,
    );
    currentConversation.value!.messages.add(botMessage);

    // Salva a conversa inteira no Hive
    await _conversationBox.put(
      currentConversation.value!.boxKey,
      currentConversation.value!,
    );

    _isLoading.value = false;
    currentConversation.update((val) {}); // Força a atualização da UI
  }

  void sendPrompt(String prompt) {
    handleSubmitted(prompt);
  }

  Widget buildUserMessage(String text) {
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

  Widget buildLLMResponse(String text, int? messageId) {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 4.0),
      alignment: Alignment.centerLeft,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          RobotAvatar(),
          SizedBox(width: 8.0),
          Expanded(
            child: GestureDetector(
              onLongPress: () {
                if (messageId != null) {
                  print("Message ID: $messageId");
                  Get.dialog(
                    FeedbackDialog(
                      messageId: messageId,
                    ),
                  );
                }
              },
              child: Container(
                padding: EdgeInsets.all(12.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12.0),
                ),
                child: Text(text, style: TextStyle(fontSize: 14.0)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget buildLoadingMessage() {
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

  Future<void> sendFeedback(FeedbackModel feedback) async {
    _isFeedbackSent.value = true;
    final success = await repository.sendFeedback(feedback);
    _isFeedbackSent.value = false;
    Get.back();
    if (success) {
      // Feedback enviado com sucesso
      Get.snackbar(
        'Feedback Enviado',
        'Obrigado pelo seu feedback!',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.green.withOpacity(0.8),
        colorText: Colors.white,
      );
    } else {
      // Falha ao enviar feedback
      Get.snackbar(
        'Erro ao Enviar Feedback',
        'Por favor, tente novamente mais tarde.',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
      );
    }

    feedbackController.clear();
    _rating.value = 0.0;
  }

  final RxDouble _rating = 0.0.obs;
  double get rating => _rating.value;

  void setRating(double value) {
    _rating.value = value;
  }
}
