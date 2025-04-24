import 'package:farmacia/app/ui/widgets/rating_buttons.dart';
import 'package:flutter/material.dart';

class QuizCard extends StatefulWidget {
  @override
  _QuizCardState createState() => _QuizCardState();
}

class _QuizCardState extends State<QuizCard> {
  int selected = 4;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.white,
      elevation: 4,
      margin: const EdgeInsets.all(32),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Navigation & Page count
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: const [
                Icon(Icons.arrow_back_ios),
                Text("1/5", style: TextStyle(fontWeight: FontWeight.bold)),
                Icon(Icons.arrow_forward_ios),
              ],
            ),
            const SizedBox(height: 20),

            Image.asset('assets/no_alcohol.png', height: 80),

            const SizedBox(height: 20),

            const Text(
              "Evito comportamentos que podem prejudicar a minha saúde (ex. tabaco, álcool)",
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 20),

            // Rating buttons
            RatingButtons(),

            const SizedBox(height: 20),

            // Legend
            const Text(
              "1 = Discordo totalmente;\n"
              "2 = Discordo moderadamente;\n"
              "3 = Discordo ligeiramente;\n"
              "4 = Não concordo nem discordo;\n"
              "5 = Concordo ligeiramente;\n"
              "6 = Concordo moderadamente;\n"
              "7 = Concordo totalmente",
              style: TextStyle(fontSize: 12),
              textAlign: TextAlign.left,
            )
          ],
        ),
      ),
    );
  }
}
