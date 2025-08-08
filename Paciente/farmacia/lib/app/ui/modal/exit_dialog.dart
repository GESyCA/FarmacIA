import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class ExitDialog extends StatelessWidget {
  ExitDialog({super.key});

  final AuthService _authService = AuthService(client: Supabase.instance.client);

  @override
  Widget build(BuildContext context) {
    return Dialog(
      backgroundColor: Colors.white,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Align(
            alignment: Alignment.topRight,
            child: IconButton(
              icon: Icon(
                Icons.close,
                color: Colors.black54,
              ),
              onPressed: () {
                Navigator.pop(context);
              },
            ),
          ),
          CircleAvatar(
            backgroundColor: Colors.red[100],
            radius: 35,
            child: Icon(
              Icons.exit_to_app,
              size: 40,
              color: Color(0xFFB9160C),
            ),
          ),
          SizedBox(
            height: 12,
          ),
          Text(
            "Tem certeza que deseja sair?",
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
          SizedBox(
            height: 16,
          ),
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
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                TextButton.icon(
                  onPressed: () {
                    Get.back();
                    _authService.signOut();
                  },
                  label: Text(
                    "Sair",
                  ),
                  style: TextButton.styleFrom(
                    foregroundColor: Color(0xFFB9160C),
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                      side: BorderSide(color: Color(0xFFB9160C)),
                    ),
                  ),
                ),
                ElevatedButton.icon(
                  onPressed: () {
                    Get.back();
                  },
                  label: Text(
                    "Cancelar",
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFFB9160C),
                    foregroundColor: Colors.white,
                    padding:
                        EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ),
              ],
            ),
          )
        ],
      ),
    );
  }
}