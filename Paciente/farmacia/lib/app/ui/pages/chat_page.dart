import 'package:farmacia/app/controllers/chat_controller.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:farmacia/app/ui/widgets/custom_app_bar.dart';

class ChatPage extends GetView<ChatController> {
  const ChatPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(title: "Chat"),
      body: Container(
        padding: EdgeInsets.all(16),
        color: Colors.grey[200],
        child: Column(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Obx(() {
                return ListView(
                  reverse: true,
                  padding: EdgeInsets.symmetric(vertical: 8),
                  children: [
                    ...controller.messages,
                    _LLMFirstMessage(),
                  ],
                );
              }),
            ),
            Column(
              children: [
                Obx(() => controller.showPrompts ? _buildPromptButtons() : SizedBox.shrink()),
                SizedBox(height: 12),
                _buildInputField(),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _LLMFirstMessage() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          CircleAvatar(backgroundColor: Color(0xFFB9160C), child: Icon(Icons.person, color: Colors.white)),
          SizedBox(width: 8),
          Expanded(
            child: Container(
              padding: EdgeInsets.all(12),
              decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Olá! Eu sou uma inteligência artificial generativa desenvolvida especialmente para auxiliar...',
                    style: TextStyle(fontSize: 14),
                  ),
                  _buildBulletPoint('Análise e interpretação da bula de medicamentos.'),
                  _buildBulletPoint('Alertas relacionados ao uso do medicamento.'),
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

  Widget _buildBulletPoint(String text) {
    return Padding(
      padding: EdgeInsets.symmetric(horizontal: 4.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('• ', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
          Expanded(child: Text(text, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold))),
        ],
      ),
    );
  }

  Widget _buildPromptButtons() {
    return Row(
      children: [
        Expanded(
          child: ElevatedButton(
            onPressed: () => controller.sendPrompt('Faça um breve resumo da bula'),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: Text('Faça um breve resumo da bula'),
          ),
        ),
        SizedBox(width: 16),
        Expanded(
          child: ElevatedButton(
            onPressed: () => controller.sendPrompt('Com que frequência devo tomar'),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red, foregroundColor: Colors.white),
            child: Text('Com que frequência devo tomar'),
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
        boxShadow: [BoxShadow(color: Colors.grey.withOpacity(0.5), blurRadius: 4, offset: Offset(0, 2))],
      ),
      child: Row(
        children: [
          Icon(Icons.camera_alt, color: Colors.grey),
          SizedBox(width: 8),
          Expanded(
            child: TextField(
              controller: controller.textController,
              decoration: InputDecoration(border: InputBorder.none, hintText: 'Pergunte algo'),
              onSubmitted: controller.handleSubmitted,
            ),
          ),
          IconButton(
            icon: Icon(Icons.send, color: Colors.grey),
            onPressed: () => controller.handleSubmitted(controller.textController.text),
          ),
        ],
      ),
    );
  }
}
