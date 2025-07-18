import 'package:farmacia/app/controllers/auth_controller.dart';
import 'package:farmacia/app/ui/navigation_menu.dart';
import 'package:farmacia/app/ui/pages/login_page.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class AuthPage extends GetView<AuthController> {
  const AuthPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Obx(() {
      return controller.isAuthenticated ? NavigationMenu() : LoginPage();
    });
  }
}
