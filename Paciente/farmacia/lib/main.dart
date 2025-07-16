import 'package:farmacia/app/ui/navigation_menu.dart';
import 'package:farmacia/app/ui/pages/add_medicine_page.dart';
import 'package:farmacia/app/ui/pages/home_page.dart';
import 'package:flutter/material.dart';
import 'app/ui/pages/login_page.dart';
import 'app/ui/pages/register_page.dart';
import 'app/ui/pages/chat_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
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
        '/home': (BuildContext context) => HomePage(),
        '/navigation': (BuildContext context) => NavigationMenu(),
        '/add_medicine': (BuildContext context) => AddMedicinePage(),
      },
    );
  }
}