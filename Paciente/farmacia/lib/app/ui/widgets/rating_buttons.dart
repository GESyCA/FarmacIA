import 'package:flutter/material.dart';

class RatingButtons extends StatefulWidget {
  int selected;
  final ValueChanged<int> onChanged;

  RatingButtons({
    super.key,
    required this.selected,
    required this.onChanged,
  });

  @override
  State<RatingButtons> createState() => _RatingButtonsState();
}

class _RatingButtonsState extends State<RatingButtons> {
  @override
  Widget build(BuildContext context) {
    return Wrap(
      alignment: WrapAlignment.center,
      children: List.generate(7, (index) {
        int value = index + 1;
        bool isSelected = value == widget.selected;

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
                widget.selected = value;
              });
              widget.onChanged(value);
            },
          ),
        );
      }),
    );
  }
}
