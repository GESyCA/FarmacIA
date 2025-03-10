import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class DeleteDialog extends StatelessWidget {
  final String medicineName;
  final VoidCallback onDelete;

  const DeleteDialog({
    super.key,
    required this.medicineName,
    required this.onDelete,
  });

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
            child: SvgPicture.asset(
              "assets/alert_circle.svg",
              height: 40,
              width: 40,
            ),
          ),
          SizedBox(
            height: 12,
          ),
          Text(
            "Tem certeza que deseja excluir o medicamento $medicineName?",
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
                    Navigator.pop(context);
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
                  
                ElevatedButton.icon(
                  onPressed: () {
                    onDelete();
                    Navigator.pop(context);
                  },
                  icon: Icon(
                    Icons.delete,
                    color: Colors.white,
                  ),
                  label: Text(
                    "Deletar",
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFFB9160C),
                    foregroundColor: Colors.white,
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 10),
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
