import 'package:flutter/material.dart';
import 'package:flutter_svg/flutter_svg.dart';

class RobotAvatar extends StatelessWidget {
  const RobotAvatar({super.key});

  @override
  Widget build(BuildContext context) {
    return CircleAvatar(
            backgroundColor: Color(0xFF0A84FF),
            child: SvgPicture.asset(
              "assets/robot.svg",
              width: 24,
              height: 24,
            ),
          );
  }
}