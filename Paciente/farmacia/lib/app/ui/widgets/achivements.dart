import 'package:farmacia/app/data/models/achivement_model.dart';
import 'package:flutter/material.dart';

class Achivements extends StatelessWidget {
  Achivements({super.key});

  final List<AchivementModel> achivements = [
    AchivementModel(
      title: "Cuidado com os medicamentos",
      icon: Icons.health_and_safety,
      progress: 75,
      color: Colors.blue[100]!,
      progressColor: Colors.blue,
    ),
    AchivementModel(
      title: "Foco e disciplina",
      icon: Icons.self_improvement,
      progress: 50,
      color: Colors.green[100]!,
      progressColor: Colors.green,
    ),
    AchivementModel(
      title: "Adesão aos medicamentos",
      icon: Icons.assignment_turned_in,
      progress: 30,
      color: Colors.amber[100]!,
      progressColor: Colors.orange,
    ),
    AchivementModel(
      title: "Autocuidado",
      icon: Icons.person,
      progress: 90,
      color: Colors.red[100]!,
      progressColor: Colors.red,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      width: MediaQuery.of(context).size.width,
      height: MediaQuery.of(context).size.height,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        children: <Widget>[
          // header with tabs
          const SizedBox(
            height: 16,
          ),
          const Text(
            "CONQUISTAS",
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(
            height: 8,
          ),
          Expanded(
            child: ListView.builder(
              itemCount: achivements.length,
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              itemBuilder: (context, index) {
                return _buildAchivementCard(achivements[index]);
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAchivementCard(AchivementModel achivement) {
    return Card(
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      color: achivement.color,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            // Progress Circle
            Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 40,
                  height: 40,
                  child: CircularProgressIndicator(
                    value: achivement.progress / 100,
                    strokeWidth: 5,
                    backgroundColor: achivement.progressColor.withOpacity(0.2),
                    valueColor:
                        AlwaysStoppedAnimation(achivement.progressColor),
                  ),
                ),
                Icon(
                  achivement.icon,
                  color: achivement.progressColor.withOpacity(0.7),
                  size: 24,
                ),
              ],
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                achivement.title,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            const Icon(
              Icons.arrow_forward_ios,
              size: 16,
              color: Colors.black38,
            ),
          ],
        ),
      ),
    );
  }
}
