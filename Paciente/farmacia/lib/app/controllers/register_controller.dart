import 'package:farmacia/app/data/models/user_model.dart';
import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:farmacia/app/routes/app_routes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class RegisterController extends GetxController {

  final AuthService _authService = AuthService();

  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();
  final TextEditingController confirmPasswordController = TextEditingController();
  final TextEditingController nameController = TextEditingController();
  final TextEditingController phoneController = TextEditingController();

  final GlobalKey<FormState> _formKey = GlobalKey<FormState>();
  GlobalKey<FormState> get formKey => _formKey;

  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final _isObscure = true.obs;
  bool get isObscure => _isObscure.value;

  final _isConfirmPasswordObscure = true.obs;
  bool get isConfirmPasswordObscure => _isConfirmPasswordObscure.value;

  void toggleConfirmPasswordVisibility() {
    _isConfirmPasswordObscure.value = !_isConfirmPasswordObscure.value;
  }

  void togglePasswordVisibility() {
    _isObscure.value = !_isObscure.value;
  }

  Future<void> register() async {
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
    final confirmPassword = confirmPasswordController.text.trim();
    final name = nameController.text.trim();
    final phone = phoneController.text.trim();

    if (password != confirmPassword) {
      _isLoading.value = false;
      Get.snackbar(
        "Erro",
        "As senhas não coincidem.",
        snackPosition: SnackPosition.BOTTOM,
      );
      return;
    }

    try {
      await _authService.signUpWithDetails(UserModel(
        email: email,
        senha: password,
        nome: name,
        telefone: phone,
      ));
      _isLoading.value = false;
      Get.offNamed(Routes.login);
    } catch (e) {
      _isLoading.value = false;
      Get.snackbar(
        "Erro ao registrar",
        e.toString().replaceFirst("Exception: ", ""),
        snackPosition: SnackPosition.BOTTOM,
      );
    }
  }

}