import 'package:farmacia/app/controllers/edit_controller.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

class EditPage extends GetView<EditController> {
  const EditPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Colors.red,
        foregroundColor: Colors.white,
        centerTitle: true,
        title: Text('Medicamento'),
      ),
      body: Container(
        width: MediaQuery.of(context).size.width,
        height: MediaQuery.of(context).size.height,
        decoration: BoxDecoration(
          color: Colors.grey[200],
        ),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildTitle(),
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                  vertical: 20,
                ),
                child: Container(
                  width: MediaQuery.of(context).size.width,
                  padding: EdgeInsets.symmetric(
                    horizontal: 24,
                    vertical: 20,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Form(
                    key: controller.formKey,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            _title("Receber notificações"),
                            Obx(
                              () => Switch(
                                value: controller.recieveNotification,
                                activeColor: Colors.red,
                                onChanged: (value) {
                                  controller.setRecieveNotification(value);
                                },
                              ),
                            ),
                          ],
                        ),
                        SizedBox(
                          height: 8,
                        ),
                        Obx(
                          () => _dropDown(
                            controller.selectedFrequency,
                            controller.frequencia,
                            (value) =>
                                controller.setSelectedFrequency(value ?? ''),
                            controller.recieveNotification,
                          ),
                        ),
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
                ),
              ),
              Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 14,
                ),
                child: Container(
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
                      _inputField(controller.doseController),
                      SizedBox(
                        height: 32,
                      ),
                      _title("Forma farmacêutica"),
                      SizedBox(
                        height: 8,
                      ),
                      _dropDown(
                        controller.selectedForma,
                        controller.formasFarmaceuticas,
                        (value) => controller.setSelectedForma(value ?? ''),
                        true,
                      ),
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
                          _inputDate(
                              context, "Inicio", controller.dateController),
                          SizedBox(width: 10),
                          _inputDate(
                              context, "Fim", controller.dateEndController),
                        ],
                      ),
                      Obx(
                        () => CheckboxListTile(
                          title: Text(
                            "Tempo indeterminado",
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey[600],
                            ),
                          ),
                          value: controller.indeterminate,
                          activeColor: Colors.red,
                          onChanged: (bool? value) {
                            controller.indeterminate = value ?? false;
                          },
                          controlAffinity: ListTileControlAffinity.leading,
                        ),
                      ),
                    ],
                  ),
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
              SizedBox(
                height: 16,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Obx _saveButton(BuildContext context) {
    return Obx(() => ElevatedButton(
          onPressed: () async {
            controller.isLoading ? null : await controller.updateMedicine();
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
          child: controller.isLoading
              ? SizedBox(
                  height: 24,
                  width: 24,
                  child: CircularProgressIndicator(
                    color: Colors.white,
                  ),
                )
              : Text(
                  "Concluir",
                  style: TextStyle(
                    fontSize: 20,
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
        ));
  }

  ElevatedButton _cancelButton(BuildContext context) {
    return ElevatedButton(
      onPressed: () => Get.back(),
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

  Expanded _inputDate(BuildContext context, String label,
      TextEditingController textController) {
    return Expanded(
      child: Obx(
        () => TextFormField(
          controller: textController,
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
          enabled: !controller.indeterminate,
          onTap: () => _selectDate(context, textController),
        ),
      ),
    );
  }

  Future<void> _selectDate(
      BuildContext context, TextEditingController textController) async {
    DateTime? pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(2000),
      lastDate: DateTime(2100),
    );
    if (pickedDate != null) {
      String formattedDate = DateFormat('dd/MM/yyyy').format(pickedDate);
      textController.text = formattedDate;
    }
  }

  TextFormField _inputField(TextEditingController controller) {
    return TextFormField(
      controller: controller,
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
      validator: (value) {
        if (value == null || value.isEmpty) {
          return 'Por favor, insira a dose';
        }
        return null;
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

  DropdownButtonFormField<String> _dropDown(
      String? selectedMedication,
      List<String> selectItems,
      void Function(String?) onChanged,
      bool isEnabled) {
    return DropdownButtonFormField<String>(
      value: selectedMedication, // Default selected value
      onChanged: isEnabled ? onChanged : null,
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

  Card _buildTitle() {
    return Card(
      color: Colors.white,
      elevation: 4,
      child: Padding(
        padding: EdgeInsets.all(16),
        child: ListTile(
          leading: Image.asset(
            'assets/icone_remedio.png',
            width: 40,
            height: 40,
          ),
          title: Text(
            controller.medicine.nome,
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
      ),
    );
  }
}
