import 'package:farmacia/app/ui/widgets/rating_buttons.dart';
import 'package:flutter/material.dart';

class QuizCard extends StatefulWidget {
  final String question;
  final String imageAsset;
  final int questionNumber;
  final int totalQuestions;
  final VoidCallback onNext;
  final VoidCallback onPrevious;
  int selectedRating;
  final ValueChanged<int> onChanged;

  QuizCard({
    super.key,
    required this.question,
    required this.imageAsset,
    required this.questionNumber,
    required this.totalQuestions,
    required this.onNext,
    required this.onPrevious,
    required this.selectedRating,
    required this.onChanged,
  });

  @override
  State<QuizCard> createState() => _QuizCardState();
}

class _QuizCardState extends State<QuizCard> {
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
              children: [
                IconButton(icon: const Icon(Icons.arrow_back_ios), onPressed: widget.onPrevious),
                Text("${widget.questionNumber}/${widget.totalQuestions}", style: TextStyle(fontWeight: FontWeight.bold)),
                IconButton(icon: const Icon(Icons.arrow_forward_ios), onPressed: widget.onNext),
              ],
            ),
            const SizedBox(height: 20),

            Image.asset(widget.imageAsset, height: 80),

            const SizedBox(height: 20),

            Text(
              widget.question,
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 20),

            // Rating buttons
            RatingButtons(
              selected: widget.selectedRating,
              onChanged: (val) {
                setState(() {
                  widget.onChanged(val);
                });
              },
            ),

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
