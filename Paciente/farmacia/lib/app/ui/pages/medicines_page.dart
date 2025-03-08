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
        padding: const EdgeInsets.all(14),
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
            Flexible(
              child: Container(
                padding: EdgeInsets.zero,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.only(
                        top: 10,
                        left: 20,
                        right: 20,
                        bottom: 2,
                      ),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        crossAxisAlignment: CrossAxisAlignment.center,
                        children: [
                          Text(
                            "${_medicines.length} medicamentos",
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 18,
                            ),
                          ),
                          SizedBox(
                            width: 50,
                            height: 50,
                            child: ElevatedButton(
                              onPressed: () {
                                //Navigator.pushNamed(context, '/add_medicine');
                              },
                              style: ElevatedButton.styleFrom(
                                shape: RoundedRectangleBorder(
                                  borderRadius:
                                      BorderRadius.circular(12),
                                ),
                                backgroundColor:
                                    Color(0xFFB9160C),
                                padding: EdgeInsets.all(10),
                              ),
                              child: Icon(
                                Icons.add,
                                color: Colors.white,
                                size: 30, 
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Divider(
                      color: Colors.grey[300],
                      thickness: 1,
                    ),
                    Expanded(
                      child: ListView.builder(
                        padding: EdgeInsets.symmetric(
                          horizontal: 12,
                          vertical: 8,
                        ),
                        itemCount: _medicines.length,
                        itemBuilder: (context, index) {
                          return Card(
                            color: Colors.white,
                            child: ListTile(
                              contentPadding: EdgeInsets.symmetric(
                                horizontal: 12,
                              ),
                              leading: Container(
                                width: 40,
                                height: 40,
                                decoration: BoxDecoration(
                                  color: Color(0xFFB9160C),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Center(
                                  child: Image.asset(
                                    "assets/Edit.png",
                                    width: 24,
                                    height: 24,
                                  ),
                                ),
                              ),
                              title: Text(
                                _medicines[index].name,
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              subtitle:
                                  Text("Próximo: ${_medicines[index].nextDate}"),
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
