import 'package:flutter/material.dart';

class AchivementModel {
  final String title;
  final IconData icon;
  final double progress; // Between 0-100
  final Color color;
  final Color progressColor;

  AchivementModel({
    required this.title,
    required this.icon,
    required this.progress,
    required this.color,
    required this.progressColor,
  });
}