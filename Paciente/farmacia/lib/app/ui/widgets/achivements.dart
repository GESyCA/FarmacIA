import 'package:farmacia/app/data/models/achivement_model.dart';
import 'package:flutter/material.dart';

class Achivements extends StatelessWidget {
  Achivements({super.key});

  final List<AchivementModel> achivements = [
    AchivementModel(
      title: "Cuidado com os medicamentos",
      icon: const Icon(Icons.health_and_safety),
      progress: 75,
      color: Colors.blue[100]!,
      progressColor: Colors.blue,
    ),
    AchivementModel(
      title: "Foco e disciplina",
      icon: const Icon(Icons.self_improvement),
      progress: 50,
      color: Colors.green[100]!,
      progressColor: Colors.green,
    ),
    AchivementModel(
      title: "Adesão aos medicamentos",
      icon: const Icon(Icons.assignment_turned_in),
      progress: 30,
      color: Colors.amber[100]!,
      progressColor: Colors.orange,
    ),
    AchivementModel(
      title: "Autocuidado",
      icon: const Icon(Icons.person),
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
            height: 16,
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
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: achivement.color,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: <Widget>[
          achivement.icon,
          const SizedBox(
            width: 16,
          ),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(
                  achivement.title,
                  style: const TextStyle(
                    fontSize: 14,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(
                  height: 8,
                ),
                LinearProgressIndicator(
                  value: achivement.progress / 100,
                  backgroundColor: achivement.color,
                  valueColor: AlwaysStoppedAnimation<Color>(achivement.progressColor),
                ),
              ],
            ),
          ),
          Text(
            "${achivement.progress}%",
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

}
