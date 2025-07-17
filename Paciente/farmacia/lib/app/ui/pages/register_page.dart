import 'package:farmacia/app/routes/app_routes.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  bool _isObscuredPassword = true; // Controls whether the text is hidden
  bool _isObscuredConfirm = true;

  void _togglePassword() {
    setState(() {
      _isObscuredPassword = !_isObscuredPassword;
    });
  }

  void _toggleConfirm() {
    setState(() {
      _isObscuredConfirm = !_isObscuredConfirm;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: SingleChildScrollView(
        child: Container(
          height: MediaQuery.of(context).size.height,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    const SizedBox(
                      height: 60,
                    ),
                    Image.asset(
                      "assets/Label.png",
                      height: 80,
                    ),
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
                    SizedBox(
                      height: 16,
                    ),
                    emailInput("Nome"),
                    SizedBox(
                      height: 24,
                    ),
                    emailInput("Email"),
                    SizedBox(
                      height: 24,
                    ),
                    emailInput("Telefone"),
                    SizedBox(
                      height: 24,
                    ),
                    senhaInput(
                      _isObscuredPassword,
                      "Senha",
                      _togglePassword,
                    ),
                    SizedBox(
                      height: 24,
                    ),
                    senhaInput(
                      _isObscuredConfirm,
                      "Confirmar Senha",
                      _toggleConfirm,
                    ),
                    SizedBox(
                      height: 24,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        ElevatedButton(
                          onPressed: () {},
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
                          child: Text(
                            "Registrar",
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.white,
                            ),
                          ),
                        ),
                      ],
                    ),
                    SizedBox(
                      height: 8,
                    ),
                    Center(
                      child: TextButton(
                          onPressed: () {
                            Get.offNamed(Routes.login); // Navigate to the login page
                          },
                          child: Text(
                            "Já tem uma conta? Login",
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Colors.white,
                              fontSize: 16,
                            ),
                          )),
                    ),
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }

  Container emailInput(String placeholder) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white, // Background color of the TextField
        borderRadius: BorderRadius.circular(12), // Rounded corners
        boxShadow: [
          BoxShadow(
            // ignore: deprecated_member_use
            color: Colors.black.withOpacity(0.2), // Shadow color
            blurRadius: 6, // Spread of the shadow
            offset:
                Offset(0, 3), // Position of the shadow (horizontal, vertical)
          ),
        ],
      ),
      child: TextField(
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        ),
      ),
    );
  }

  Container senhaInput(
      bool isObscured, String placeholder, VoidCallback onToggle) {
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
      child: TextField(
        obscureText: isObscured, // Hides or shows the password
        decoration: InputDecoration(
          labelText: placeholder,
          border: InputBorder.none,
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          suffixIcon: IconButton(
            icon: Icon(
              isObscured ? Icons.visibility_off : Icons.visibility,
            ),
            onPressed: onToggle,
          ),
        ),
      ),
    );
  }
}