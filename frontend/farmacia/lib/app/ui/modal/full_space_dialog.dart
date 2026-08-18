import 'package:flutter/material.dart';
import 'package:get/get.dart';

class FullSpaceDialog extends StatelessWidget {
  const FullSpaceDialog({super.key});

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
              Icons.folder_copy_outlined,
              color: Color(0xFFB9160C),
              size: 40,
            ),
          ),
          SizedBox(
            height: 12,
          ),
          Text(
            "Você já possui todos os medicamentos disponíveis",
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
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                TextButton.icon(
                  onPressed: () {
                    Get.back();
                  },
                  icon: Icon(
                    Icons.close,
                    color: Color(0xFFB9160C),
                  ),
                  label: Text(
                    "Cancelar",
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
              ],
            ),
          )
        ],
      ),
    );
  }
}