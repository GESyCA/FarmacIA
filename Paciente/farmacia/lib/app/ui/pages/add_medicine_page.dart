import 'package:flutter/material.dart';

class AddMedicinePage extends StatefulWidget {
  const AddMedicinePage({super.key});

  @override
  State<AddMedicinePage> createState() => _AddMedicinePageState();
}

class _AddMedicinePageState extends State<AddMedicinePage> {
  String? selectedMedication = "Dipirona";
  bool receiveNotifications = true;
  String? selectedFrequency = "3 vezes ao dia";
  String dose = "500 mg";
  String? selectedForm = "Comprimido";
  DateTime? selectedDate;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        centerTitle: true,
        title: const Text("Cadastro"),
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
        padding: const EdgeInsets.symmetric(
          horizontal: 14,
          vertical: 24,
        ),
        decoration: BoxDecoration(
          color: Colors.grey[200],
        ),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                width: MediaQuery.of(context).size.width,
                padding: EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 20,
                ),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "Medicamento",
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(
                      height: 8,
                    ),
                    _dropDown(
                        "Dipirona", ["Dipirona", "Paracetamol", "Ibuprofeno"]),
                    SizedBox(
                      height: 32,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          "Receber notificações",
                          style: TextStyle(
                            fontSize: 17,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Switch(
                          value: receiveNotifications,
                          activeColor: Colors.red,
                          onChanged: (value) {
                            setState(() {
                              receiveNotifications = value;
                            });
                          },
                        ),
                      ],
                    ),
                    SizedBox(
                      height: 8,
                    ),
                    _dropDown("3 vezes ao dia",
                        ["3 vezes ao dia", "2 vezes ao dia", "1 vez ao dia"]),
                    SizedBox(
                      height: 32,
                    ),
                    Text(
                      "Horários de lembrete",
                      style: TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(
                      height: 8,
                    ),
                    _reminderCard(
                        time: "7:00", description: "Tomar 1 comprimido"),
                    SizedBox(height: 10),
                    _reminderCard(
                        time: "15:00", description: "Tomar 1 comprimido"),
                    SizedBox(height: 10),
                    _reminderCard(
                        time: "23:00", description: "Tomar 1 comprimido"),
                  ],
                ),
              )
            ],
          ),
        ),
      ),
    );
  }

  DropdownButtonFormField<String> _dropDown(
      String? selectedMedication, List<String> selectItems) {
    return DropdownButtonFormField<String>(
      value: selectedMedication, // Default selected value
      onChanged: (newValue) {
        // Handle value change
      },
      items: selectItems
          .map((med) => DropdownMenuItem(
                value: med,
                child: Text(med,
                    style: TextStyle(fontSize: 16, color: Colors.black87)),
              ))
          .toList(),
      decoration: InputDecoration(
        contentPadding: EdgeInsets.symmetric(
            horizontal: 16, vertical: 14),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(12),
          borderSide: BorderSide(color: Colors.grey), // Highlight on focus
        ),
      ),
      icon: Icon(Icons.arrow_drop_down,
          color: Colors.black), // Custom dropdown icon
      dropdownColor: Colors.white, // Background of dropdown menu
    );
  }

  Card _reminderCard({required String time, required String description}) {
    return Card(
      color: Colors.white,
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: Padding(padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          
          children: [
            Text(
              time,
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.w600,
              ),
            ),
            Text(
              description,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
