import 'package:farmacia/app/controllers/auth_controller.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class ExitDialog extends StatelessWidget {
  const ExitDialog({super.key});


  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          SizedBox(height: 40),
          CircleAvatar(
            backgroundColor: Colors.red[100],
            radius: 35,
            child: Icon(Icons.exit_to_app, size: 40, color: Color(0xFFB9160C)),
          ),
          SizedBox(height: 12),
          Text(
            "Tem certeza que deseja sair?",
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          SizedBox(height: 16),
          Container(
            width: double.infinity,
            height: 80,
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.only(
                bottomLeft: Radius.circular(20),
                bottomRight: Radius.circular(20),
              ),
            ),
            child: GetBuilder<AuthController>(
              init: AuthController(),
              builder: (controller) {
                return Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    TextButton.icon(
                      onPressed: controller.isLoading ? null : () {
                        controller.signOut();
                      },
                      label: controller.isLoading ? SizedBox(height: 20, width: 20, child: CircularProgressIndicator()) : Text("Sair"),
                      style: TextButton.styleFrom(
                        foregroundColor: Color(0xFFB9160C),
                        padding: EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                          side: BorderSide(color: Color(0xFFB9160C)),
                        ),
                      ),
                    ),
                    ElevatedButton.icon(
                      onPressed: controller.isLoading ? null : () {
                        Get.back();
                      },
                      label: Text("Cancelar"),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Color(0xFFB9160C),
                        foregroundColor: Colors.white,
                        padding: EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
