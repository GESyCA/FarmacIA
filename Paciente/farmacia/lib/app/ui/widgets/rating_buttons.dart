import 'package:flutter/material.dart';

class RatingButtons extends StatefulWidget {
  const RatingButtons({super.key});

  @override
  State<RatingButtons> createState() => _RatingButtonsState();
}

class _RatingButtonsState extends State<RatingButtons> {
  int _selected = 4;
  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,

      children: List.generate(7, (index) {
        int value = index + 1;
        bool isSelected = value == _selected;

        return Padding(
          padding: const EdgeInsets.symmetric(horizontal: 4),
          child: ChoiceChip(
            label: Text(
              value.toString(),
              style: TextStyle(
                color: isSelected ? Colors.red : Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            selected: isSelected,
            selectedColor: Colors.white,
            backgroundColor: Colors.red,
            showCheckmark: false,
            labelStyle: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(20),
              side: isSelected
                  ? const BorderSide(color: Colors.red, width: 2)
                  : BorderSide.none,
            ),
            onSelected: (_) {
              setState(() {
                _selected = value;
              });
            },
          ),
        );
      }),
    );
  }
}
