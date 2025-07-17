import 'package:farmacia/app/data/models/medicine.dart';
import 'package:flutter/material.dart';

class Statistics extends StatelessWidget {
  final List<Medicine> _medicines = [
    Medicine(id: 1, name: "Paracetamol", nextDate: "10/10/2025 07:00"),
    Medicine(id: 2, name: "Ibuprofeno", nextDate: "10/10/2025 07:00"),
    Medicine(id: 3, name: "Omeprazol", nextDate: "10/10/2025 07:00"),
    Medicine(id: 4, name: "Amoxilinina", nextDate: "10/10/2025 07:00"),
  ];

  Statistics({super.key});

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
            "INFORMAÇÕES",
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(
            height: 20,
          ),
          Expanded(
            child: ListView.builder(
              itemCount: _medicines.length,
              itemBuilder: (context, index) {
                final medicine = _medicines[index];
                return Column(
                  children: [
                    Card(
                      color: Colors.grey[100],
                      child: ListTile(
                        leading: const Icon(
                          Icons.medication,
                          color: Colors.red,
                        ),
                        title: Text(medicine.name,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            )),
                        trailing: IconButton(
                          icon: const Icon(
                            Icons.arrow_forward_ios,
                            size: 16,
                          ),
                          onPressed: () {
                            // TODO: Navigate to medicine details
                          },
                        ),
                      ),
                    ),
                    const SizedBox(
                      height: 12,
                    ),
                  ],
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
