import 'package:farmacia/app/ui/widgets/custom_app_bar.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

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

  final _dateController = TextEditingController();
  final _endDateController = TextEditingController();
  bool _indeterminate = false;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: CustomAppBar(title: 'Adicionar Medicamento'),
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
                    _title("Medicamento"),
                    SizedBox(
                      height: 8,
                    ),
                    _dropDown(
                        "Dipirona",
                        ["Dipirona", "Paracetamol", "Ibuprofeno"],
                        selectedMedication!),
                    SizedBox(
                      height: 32,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _title("Receber notificações"),
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
                    _dropDown(
                        "3 vezes ao dia",
                        ["3 vezes ao dia", "2 vezes ao dia", "1 vez ao dia"],
                        selectedFrequency!),
                    SizedBox(
                      height: 32,
                    ),
                    _title("Horários de lembrete"),
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
              ),
              SizedBox(
                height: 24,
              ),
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
                    _title("Dose"),
                    SizedBox(
                      height: 8,
                    ),
                    _inputField(),
                    SizedBox(
                      height: 32,
                    ),
                    _title("Forma farmacêutica"),
                    SizedBox(
                      height: 8,
                    ),
                    _dropDown("Comprimido", ["Comprimido", "Gotas", "Pomada"],
                        selectedForm!),
                    SizedBox(
                      height: 32,
                    ),
                    _title("Duração do tratamento"),
                    SizedBox(
                      height: 8,
                    ),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _inputDate(context, "Inicio", _dateController),
                        SizedBox(width: 10),
                        _inputDate(context, "Fim", _endDateController),
                      ],
                    ),
                    CheckboxListTile(
                      title: Text(
                        "Tempo indeterminado",
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.grey[600],
                        ),
                      ),
                      value: _indeterminate,
                      activeColor: Colors.red,
                      onChanged: (bool? value) {
                        setState(() {
                          _indeterminate = value ?? false;
                        });
                      },
                      controlAffinity: ListTileControlAffinity.leading,
                    ),
                  ],
                ),
              ),
              SizedBox(
                height: 16,
              ),
              // Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _cancelButton(context),
                  _saveButton(context),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  ElevatedButton _saveButton(BuildContext context) {
    return ElevatedButton(
                  onPressed: () {
                    // Save medicine
                    Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Color(0xFFB9160C),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                  ),
                  child: Text(
                    "Concluir",
                    style: TextStyle(
                      fontSize: 20,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                );
  }

  ElevatedButton _cancelButton(BuildContext context) {
    return ElevatedButton(
                  onPressed: () => Navigator.pop(context),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(color: Color(0xFFB9160C)),
                    ),
                    padding: EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                  ),
                  child: Text(
                    "Cancelar",
                    style: TextStyle(
                      fontSize: 20,
                      color: Color(0xFFB9160C),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                );
  }

  Expanded _inputDate(
      BuildContext context, String label, TextEditingController controller) {
    return Expanded(
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(
          labelText: label,
          hintText: "MM/DD/YYYY",
          contentPadding: EdgeInsets.symmetric(
            horizontal: 16,
            vertical: 14,
          ),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: Colors.grey),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: Colors.grey),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(8),
            borderSide: BorderSide(color: Colors.red),
          ),
        ),
        readOnly: true,
        enabled: !_indeterminate,
        onTap: () => _selectDate(context, controller),
      ),
    );
  }

  Future<void> _selectDate(
      BuildContext context, TextEditingController controller) async {
    DateTime? pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (pickedDate != null) {
      String formattedDate = DateFormat('dd/MM/yyyy').format(pickedDate);
      setState(() {
        controller.text = formattedDate;
      });
    }
  }

  TextField _inputField() {
    return TextField(
      decoration: InputDecoration(
        hintText: "500 mg",
        contentPadding: EdgeInsets.symmetric(
          horizontal: 16,
          vertical: 14,
        ),
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
          borderSide: BorderSide(color: Colors.grey),
        ),
      ),
      onChanged: (value) {
        setState(() {
          dose = value;
        });
      },
    );
  }

  Text _title(String title) {
    return Text(
      title,
      style: TextStyle(
        fontSize: 17,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  DropdownButtonFormField<String> _dropDown(String? selectedMedication,
      List<String> selectItems, String controlVariable) {
    return DropdownButtonFormField<String>(
      value: selectedMedication, // Default selected value
      onChanged: (newValue) {
        // Handle value change
        setState(() {
          controlVariable = newValue!;
        });
      },
      items: selectItems
          .map((med) => DropdownMenuItem(
                value: med,
                child: Text(med,
                    style: TextStyle(fontSize: 16, color: Colors.grey[600])),
              ))
          .toList(),
      decoration: InputDecoration(
        contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 14),
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
      child: Padding(
        padding: EdgeInsets.symmetric(vertical: 8, horizontal: 12),
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
