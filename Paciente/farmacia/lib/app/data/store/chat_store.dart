import 'package:farmacia/app/data/repositories/chat_repository.dart';
import 'package:flutter/material.dart';

class ChatStore {
  final ChatRepository chatRepository;

  ChatStore({required this.chatRepository});

  // variavel reativa para o loading
  final ValueNotifier loading = ValueNotifier<bool>(false);

  // variavel reativa para a resposta
  final ValueNotifier<String> answer = ValueNotifier<String>('');
}