import 'package:farmacia/app/controllers/register_controller.dart';
import 'package:farmacia/app/routes/app_routes.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';

class RegisterPage extends GetView<RegisterController> {
  const RegisterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: SizedBox(
          height: MediaQuery.of(context).size.height,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(height: 60),
                    Image.asset("assets/Label.png", height: 80),
                  ],
                ),
              ),
              Container(
                width: MediaQuery.of(context).size.width,
                padding: EdgeInsets.symmetric(horizontal: 24, vertical: 32),
                decoration: BoxDecoration(
                  color: Colors.red,
                  borderRadius: BorderRadius.only(
                    topLeft: Radius.circular(48),
                    topRight: Radius.circular(48),
                  ),
                ),
                child: Form(
                  key: controller.formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "Cadastro",
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      SizedBox(height: 16),
                      nomeInput("Nome", controller.nameController),
                      SizedBox(height: 24),
                      emailInput("Email", controller.emailController),
                      SizedBox(height: 24),
                      telefoneInput("Telefone", controller.phoneController),
                      SizedBox(height: 24),
                      Obx(
                        () =>
                            senhaInput("Senha", controller.passwordController),
                      ),
                      SizedBox(height: 24),
                      Obx(
                        () => confirmaSenhaInput(
                          "Confirmar senha",
                          controller.confirmPasswordController,
                        ),
                      ),
                      SizedBox(height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Obx(
                            () => ElevatedButton(
                              onPressed:
                                  () =>
                                      controller.isLoading
                                          ? null
                                          : controller.register(),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: Color(0xFF2656E6),
                                padding: EdgeInsets.symmetric(
                                  vertical: 12,
                                  horizontal: 48,
                                ),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(24),
                                ),
                                elevation: 4,
                              ),
                              child:
                                  controller.isLoading
                                      ? SizedBox(
                                        height: 20,
                                        width: 20,
                                        child: CircularProgressIndicator(
                                          color: Colors.white,
                                        ),
                                      )
                                      : Text(
                                        "Registrar",
                                        style: TextStyle(
                                          fontSize: 20,
                                          fontWeight: FontWeight.bold,
                                          color: Colors.white,
                                        ),
                                      ),
                            ),
                          ),
                        ],
                      ),
                      SizedBox(height: 8),
                      Center(
                        child: TextButton(
                          onPressed: () {
                            Get.offNamed(
                              Routes.login,
                            ); // Navigate to the login page
                          },
                          child: Text(
                            "Já tem uma conta? Login",
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white, fontSize: 16),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Container emailInput(String placeholder, TextEditingController controller) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white, // Background color of the TextField
        borderRadius: BorderRadius.circular(12), // Rounded corners
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.2), // Shadow color
            blurRadius: 6, // Spread of the shadow
            offset: Offset(
              0,
              3,
            ), // Position of the shadow (horizontal, vertical)
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        keyboardType: TextInputType.emailAddress,
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Por favor, preencha este campo.';
          }
          if (placeholder == "Email" && !GetUtils.isEmail(value)) {
            return 'Por favor, insira um email válido.';
          }
          return null;
        },
      ),
    );
  }

  Container nomeInput(String placeholder, TextEditingController controller) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white, // Background color of the TextField
        borderRadius: BorderRadius.circular(12), // Rounded corners
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.2), // Shadow color
            blurRadius: 6, // Spread of the shadow
            offset: Offset(
              0,
              3,
            ), // Position of the shadow (horizontal, vertical)
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Por favor, preencha este campo.';
          }
          return null;
        },
      ),
    );
  }

  Container telefoneInput(
    String placeholder,
    TextEditingController controller,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white, // Background color of the TextField
        borderRadius: BorderRadius.circular(12), // Rounded corners
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.2), // Shadow color
            blurRadius: 6, // Spread of the shadow
            offset: Offset(
              0,
              3,
            ), // Position of the shadow (horizontal, vertical)
          ),
        ],
      ),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
        keyboardType: TextInputType.phone,
        inputFormatters: [
               FilteringTextInputFormatter.digitsOnly,
              LengthLimitingTextInputFormatter(11), // Limit to 11 digits
              TelefoneInputFormatter()
            ],
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Por favor, preencha este campo.';
          }
          if (!RegExp(r'^\(\d{2}\) \d{5}-\d{4}$').hasMatch(value)) {
            return 'Formato do Telefone inválido.';
          }
          return null;
        },
      ),
    );
  }

  Container senhaInput(
    String placeholder,
    TextEditingController textController,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.2),
            blurRadius: 6,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: TextFormField(
        controller: textController,
        obscureText: controller.isObscure, // Hides or shows the password
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          suffixIcon: IconButton(
            icon: Icon(
              controller.isObscure ? Icons.visibility_off : Icons.visibility,
            ),
            onPressed: () => controller.togglePasswordVisibility(),
          ),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Por favor, preencha este campo.';
          }
          if (value.length < 6) {
            return 'A senha deve ter pelo menos 6 caracteres.';
          }
          return null;
        },
      ),
    );
  }

  Container confirmaSenhaInput(
    String placeholder,
    TextEditingController textController,
  ) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.2),
            blurRadius: 6,
            offset: Offset(0, 3),
          ),
        ],
      ),
      child: TextFormField(
        controller: textController,
        obscureText:
            controller.isConfirmPasswordObscure, // Hides or shows the password
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          suffixIcon: IconButton(
            icon: Icon(
              controller.isConfirmPasswordObscure
                  ? Icons.visibility_off
                  : Icons.visibility,
            ),
            onPressed: () => controller.toggleConfirmPasswordVisibility(),
          ),
        ),
        validator: (value) {
          if (value == null || value.isEmpty) {
            return 'Por favor, preencha este campo.';
          }
          if (value.length < 6) {
            return 'A senha deve ter pelo menos 6 caracteres.';
          }
          return null;
        },
      ),
    );
  }
}

class TelefoneInputFormatter extends TextInputFormatter {
  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    String digitsOnly = newValue.text.replaceAll(RegExp(r'\D'), '');
    if (digitsOnly.length > 11) {
      digitsOnly = digitsOnly.substring(0, 11);
    }

    String formatted = digitsOnly;

    if (digitsOnly.length >= 11) {
      formatted =
          '(${digitsOnly.substring(0, 2)}) ${digitsOnly.substring(2, 7)}-${digitsOnly.substring(7)}';
    } else if (digitsOnly.length >= 7) {
      formatted =
          '(${digitsOnly.substring(0, 2)}) ${digitsOnly.substring(2, 6)}-${digitsOnly.substring(6)}';
    } else if (digitsOnly.length >= 3) {
      formatted =
          '(${digitsOnly.substring(0, 2)}) ${digitsOnly.substring(2)}';
    } else if (digitsOnly.length >= 1) {
      formatted = '(${digitsOnly.substring(0, digitsOnly.length)}';
    }

    return TextEditingValue(
      text: formatted,
      selection: TextSelection.collapsed(offset: formatted.length),
    );
  }
}
