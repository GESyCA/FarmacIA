import 'package:hive/hive.dart';

part 'conversation_model.g.dart'; // Este arquivo será gerado

@HiveType(typeId: 1)
class ChatMessage {
  @HiveField(0)
  final String text;

  @HiveField(1)
  final bool isUserMessage;

  @HiveField(2)
  final DateTime timestamp;

  @HiveField(3)
  final int? messageId;

  @HiveField(4)
  bool feedbackGiven;

  ChatMessage({
    required this.text,
    required this.isUserMessage,
    required this.timestamp,
    this.messageId,
    this.feedbackGiven = false,
  });
}

@HiveType(typeId: 2)
class Conversation extends HiveObject {
  @HiveField(0)
  String? conversationId; // Pode ser nulo no início

  @HiveField(1)
  final String medicineName;

  @HiveField(2)
  final String userId;

  @HiveField(3)
  List<ChatMessage> messages;

  Conversation({
    this.conversationId,
    required this.medicineName,
    required this.userId,
    required this.messages,
  });

  // Chave única para salvar/recuperar no Hive
  String get boxKey => '${userId}_$medicineName';
}