import 'package:flutter/material.dart';
import 'login_page.dart';
import 'register_page.dart';
import 'chat_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.deepPurple),
        useMaterial3: true,
      ),
      home: const LoginPage(),
      routes: <String, WidgetBuilder>{
        '/register': (BuildContext context) => RegisterPage(),
        '/login': (BuildContext context) => LoginPage(),
        '/chat': (BuildContext context) => ChatPage(),
      },
    );
  }
}