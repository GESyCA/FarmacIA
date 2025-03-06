import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:flutter/material.dart';

class MedicinesPage extends StatefulWidget {
  const MedicinesPage({super.key});

  @override
  State<MedicinesPage> createState() => _MedicinesPageState();
}

class _MedicinesPageState extends State<MedicinesPage> {
  final List<Medicine> _medicines = [
    Medicine(id: 1, name: "Paracetamol", nextDate: "10/10/2025 07:00"),
    Medicine(id: 2, name: "Ibuprofeno", nextDate: "10/10/2025 07:00"),
    Medicine(id: 3, name: "Omeprazol", nextDate: "10/10/2025 07:00"),
    Medicine(id: 4, name: "Amoxilinina", nextDate: "10/10/2025 07:00"),
    Medicine(id: 5, name: "Dipirona", nextDate: "10/10/2025 07:00"),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        centerTitle: true,
        title: const Text("Medicamentos"),
        actions: [
          IconButton(
            icon: const Icon(Icons.account_circle),
            onPressed: () {
              Navigator.pushNamed(context, '/login');
            },
          ),
        ],
      ),
      body: Container(
        width: MediaQuery.of(context).size.width,
        height: MediaQuery.of(context).size.height,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.grey[200],
        ),
        child: Column(
          children: [
            SizedBox(
              height: 16,
            ),
            _searchBar(),
            SizedBox(
              height: 16,
            ),
            Expanded(
              child: ListView.builder(
                itemCount: _medicines.length,
                itemBuilder: (context, index) {
                  return Card(
                    color: Colors.white,
                    child: ListTile(
                      leading: Icon(
                        Icons.edit,
                        color: Colors.red,
                      ),
                      title: Text(_medicines[index].name),
                      subtitle: Text(_medicines[index].nextDate),
                      trailing: IconButton(
                        icon: const Icon(
                          Icons.delete,
                          color: Colors.red,
                        ),
                        onPressed: () {
                          setState(() {
                            _medicines.removeAt(index);
                          });
                        },
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  TextField _searchBar() {
    return TextField(
      decoration: InputDecoration(
        hintText: "Buscar por medicamento",
        prefixIcon: Icon(Icons.search),
        suffixIcon: Icon(Icons.mic),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Color(0xFFCBD5E1)),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Color(0xFFCBD5E1)),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Color(0xFFCBD5E1), width: 2),
        ),
        filled: true,
        fillColor: Colors.white,
      ),
    );
  }
}
