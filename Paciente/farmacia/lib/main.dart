import 'package:farmacia/app/app_widget.dart';
import 'package:farmacia/app/data/models/hive/conversation_model.dart';
import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Inicializa o Hive
  await Hive.initFlutter();

  // Registra os adaptadores gerados
  Hive.registerAdapter(ChatMessageAdapter());
  Hive.registerAdapter(ConversationAdapter());

  // Abre o box que vai guardar as conversas
  await Hive.openBox<Conversation>('conversations');

  // load env
  await dotenv.load(fileName: ".env");
  // initialize supabase
  String supabaseUrl = dotenv.env['SUPABASE_URL'] ?? '';
  String supabaseKey = dotenv.env['SUPABASE_KEY'] ?? '';
  await Supabase.initialize(
    url: supabaseUrl,
    anonKey: supabaseKey,
  );
  
  runApp(const MyApp());
}

