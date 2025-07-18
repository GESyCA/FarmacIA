import 'package:farmacia/app/controllers/medicine_controller.dart';
import 'package:farmacia/app/data/http/http_client.dart';
import 'package:farmacia/app/data/models/question_model.dart';
import 'package:farmacia/app/data/repositories/chat_repository.dart';
import 'package:farmacia/app/ui/widgets/custom_app_bar.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ChatPage extends StatefulWidget {
  const ChatPage({super.key});

  @override
  State<ChatPage> createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  final TextEditingController _textController = TextEditingController();
  final ValueNotifier<List<Widget>> _messagesNotifier = ValueNotifier([]);
  bool _showPrompts = true;

  // final MedicineController _medicineController = Get.find<MedicineController>();
  // List<String> medicinesAvailable = []; 

  // Future<void> _fetchAvailableMedicines() {

  // }

  final ChatRepository _chatRepository = ChatRepository(
    httpClient: HttpClient(
      baseUrl: "https://086eb0217e49.ngrok-free.app",
    ),
  );

  String nomeRemedio = "Paracetamol"; // Example medicine name

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(title: "Chat"),
      body: LayoutBuilder(
        builder: (context, constraints) {
          return Container(
            width: constraints.maxWidth,
            height: constraints.maxHeight,
            padding: EdgeInsets.all(16.0),
            decoration: BoxDecoration(
              color: Colors.grey[200],
            ),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: ValueListenableBuilder<List<Widget>>(
                    valueListenable: _messagesNotifier,
                    builder: (context, messages, child) {
                      return ListView(
                        reverse: true, // Keeps latest messages at the bottom
                        padding: EdgeInsets.symmetric(vertical: 8.0),
                        children: [
                          ...messages, // Dynamically updates messages
                          _LLMFirstMessage(),
                        ],
                      );
                    },
                  ),
                ),
                Column(
                  children: [
                    if (_showPrompts) _buildPromptButtons(),
                    SizedBox(height: 12.0),
                    _buildInputField(),
                  ],
                )
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _handleSubmitted(String text) async {
    if (text.isEmpty) return;

    _textController.clear();
    setState(() {
      _showPrompts = false;
    });

    // Get current messages and add user message
    List<Widget> currentMessages = List.from(_messagesNotifier.value);
    currentMessages.insert(0, _buildUserMessage(text));

    // Add "Thinking..." message
    final loadingMessage = _buildLoadingMessage();
    currentMessages.insert(0, loadingMessage);
    _messagesNotifier.value = currentMessages;

    // Fetch API response
    final answer = await _chatRepository.sendMessage(QuestionModel(
      nomeRemedio: nomeRemedio,
      pergunta: text,
    ));

    // Replace loading message with actual response
    currentMessages = List.from(_messagesNotifier.value);
    currentMessages.remove(loadingMessage); // Remove the loading state
    currentMessages.insert(0, _buildLLMResponse(answer.resposta));

    // Update messages
    _messagesNotifier.value = currentMessages;
  }

  void _sendPrompt(String prompt) {
    _handleSubmitted(prompt);
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

  Widget _buildBulletPoint(String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text('• ',
              style: TextStyle(
                fontSize: 14.0,
                fontWeight: FontWeight.bold,
              )),
          Expanded(
            child: Text(
              text,
              style: TextStyle(
                fontSize: 14.0,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _LLMFirstMessage() {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 4.0),
      alignment: Alignment.centerLeft,
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(
            backgroundColor: Color(0xFFB9160C),
            child: Icon(Icons.person, color: Colors.white),
          ),
          SizedBox(width: 8.0),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Olá! Eu sou uma inteligência artificial generativa desenvolvida especialmente para auxiliar no seu acompanhamento farmacêutico. Minha função é garantir que você receba o melhor suporte possível no uso de medicamentos, com segurança e precisão. Estou aqui para ajudar você principalmente nos seguinte pontos:',
                    style: TextStyle(fontSize: 14.0),
                  ),
                  _buildBulletPoint(
                      'Análise e interpretação da bula de medicamentos.'),
                  _buildBulletPoint(
                      'Alertas relacionados ao uso do medicamento.'),
                  _buildBulletPoint('Informações de acesso ao medicamento.'),
                  _buildBulletPoint('Dosagem adequada do medicamento.'),
                  _buildBulletPoint('Dentre outros.'),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPromptButtons() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton(
            onPressed: () => _sendPrompt('Faça um breve resumo da bula'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              padding: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
            ),
            child: Container(
              width: double.infinity, // Allow the container to take full width
              child: Text(
                'Faça um breve resumo da bula',
                textAlign:
                    TextAlign.start, // Center the text and allow wrapping
                softWrap: true, // Enable text wrapping
              ),
            ),
          ),
        ),
        SizedBox(width: 28.0), // Add spacing between buttons
        Expanded(
          child: ElevatedButton(
            onPressed: () => _sendPrompt('Com que frequencia devo tomar'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
              padding: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12.0),
              ),
            ),
            child: Container(
              width: double.infinity, // Allow the container to take full width
              child: Text(
                'Com que frequencia devo tomar',
                textAlign:
                    TextAlign.start, // Center the text and allow wrapping
                softWrap: true, // Enable text wrapping
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildInputField() {
    return Container(
      padding: EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: Colors.grey.withOpacity(0.5),
            blurRadius: 4,
            offset: Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Icon(Icons.camera_alt, color: Colors.grey),
          SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: _textController,
              decoration: InputDecoration(
                border: InputBorder.none,
                hintText: 'Pergunte algo',
                hintStyle: TextStyle(color: Colors.grey),
              ),
              onSubmitted: _handleSubmitted,
            ),
          ),
          IconButton(
            icon: Icon(Icons.send, color: Colors.grey),
            onPressed: () => _handleSubmitted(_textController.text),
          ),
        ],
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
          CircleAvatar(
            backgroundColor: Color(0xFFB9160C),
            child: Icon(Icons.person, color: Colors.white),
          ),
          SizedBox(width: 8.0),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    text,
                    style: TextStyle(fontSize: 14.0),
                  ),
                ],
              ),
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
          CircleAvatar(
            backgroundColor: Color(0xFFB9160C),
            child: Icon(Icons.person, color: Colors.white),
          ),
          SizedBox(width: 8.0),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(12.0),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(12.0),
              ),
              child: Row(
                children: [
                  _buildTypingIndicator(), // Animation for typing effect
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  _buildTypingIndicator() {
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
