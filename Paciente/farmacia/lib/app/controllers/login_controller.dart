import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class LoginController extends GetxController {
  // Define any necessary variables and methods for the login functionality here
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  //form key
  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  GlobalKey<FormState> get formKey => _formKey;

  final _isObscure = true.obs;
  bool get isObscure => _isObscure.value;

  final AuthService _authService = AuthService(client: Supabase.instance.client);

  // Method to handle login
  void login() async {
    if (!(_formKey.currentState?.validate() ?? false)) {
      Get.snackbar(
        "Erro",
        "Por favor, preencha todos os campos corretamente.",
        snackPosition: SnackPosition.BOTTOM,
      );
      return;
    }

    _isLoading.value = true;

    final email = emailController.text.trim();
    final password = passwordController.text.trim();

    try {
      final response = await _authService.signIn(email, password);
      _isLoading.value = false;

      // You could check response.session as well if needed
      //Get.offNamed(Routes.navigation);
    } catch (e) {
      _isLoading.value = false;
      Get.snackbar(
        "Erro ao entrar",
        e.toString().replaceFirst("Exception: ", ""),
        snackPosition: SnackPosition.BOTTOM,
      );
    }
  }

  // Method to toggle password visibility
  void togglePasswordVisibility() {
    _isObscure.value = !_isObscure.value;
  }
}
