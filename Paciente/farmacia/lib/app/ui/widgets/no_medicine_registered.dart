import 'package:flutter/material.dart';

class NoMedicineRegistered extends StatelessWidget {
  const NoMedicineRegistered({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      physics: const AlwaysScrollableScrollPhysics(),
      children: [
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              Text(
                'Sem medicamentos cadastrados',
                style: TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.start,
              ),
              const SizedBox(
                height: 16,
              ),
              Text(
                'Comece agora o acompanhamento do seu tratamento',
                style: TextStyle(
                  fontSize: 16,
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.start,
              ),
              const SizedBox(
                height: 32,
              ),
              Image.asset(
                'assets/waiting.png',
                height: 200,
              ),
            ],
          ),
        ),
      ],
    );
  }
}