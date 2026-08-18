import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';

class EditController extends GetxController{ 
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final DatabaseService database;

  EditController(this.database);

  late MedicineModel medicine;

  // chave do formulario
  final GlobalKey<FormState> formKey = GlobalKey<FormState>();
  
  // controladores de texto para os campos do formulario
  final TextEditingController dateController = TextEditingController();
  final TextEditingController dateEndController = TextEditingController();
  final TextEditingController doseController = TextEditingController();

  // variaveis para controle de notificacoes
  final _recieveNotification = false.obs;
  bool get recieveNotification => _recieveNotification.value;
  void setRecieveNotification(bool value) {
    _recieveNotification.value = value;
  }

  // variavel para defirnir se o tratamento terá tempo indeterminado
  final _indeterminate = false.obs;
  bool get indeterminate => _indeterminate.value;
  set indeterminate(bool value) {
    _indeterminate.value = value;
  }

  List<String> frequencia = [
    '1 vez ao dia',
    '2 vezes ao dia',
    '3 vezes ao dia',
    '4 vezes ao dia',
  ];

  final RxString _selectedFrequency = ''.obs;
  String get selectedFrequency => _selectedFrequency.value;
  void setSelectedFrequency(String value) {
    _selectedFrequency.value = value;
  }

  List<String> formasFarmaceuticas = [
    'Comprimido',
    'Gotas',
    'Pomada',
  ];

  final RxString _selectedForma = ''.obs;
  String get selectedForma => _selectedForma.value;
  void setSelectedForma(String value) {
    _selectedForma.value = value;
  }

  @override
  void onInit() {
    super.onInit();
    medicine = Get.arguments;
    dateController.text = DateFormat('dd/MM/yyyy').format(medicine.inicioTratamento);
    dateEndController.text = medicine.fimTratamento != null ? DateFormat('dd/MM/yyyy').format(medicine.fimTratamento!) : '';
    doseController.text = medicine.dose.toString();
    setSelectedForma(medicine.forma);
    setSelectedFrequency(medicine.notificacoesPorDia != null ? frequencia[medicine.notificacoesPorDia! - 1] : frequencia.first);
    setRecieveNotification(medicine.receberNotificacao);
  }

  @override
  void onClose() {
    dateController.dispose();
    dateEndController.dispose();
    doseController.dispose();
    super.onClose();
  }

  void _updateMedicine() {
    
    medicine = medicine.copyWith(
      inicioTratamento: DateFormat('dd/MM/yyyy').parse(dateController.text),
      fimTratamento: _indeterminate.value 
            ? null
            : DateFormat('dd/MM/yyyy').parse(dateEndController.text),
      dose: doseController.text,
      notificacoesPorDia: _recieveNotification.value
            ? int.parse(_selectedFrequency.value.split(' ')[0])
            : null,
      forma: selectedForma,
      receberNotificacao: recieveNotification,
    );
  }

  Future<void> updateMedicine() async {
    try {
      _isLoading.value = true;
      _updateMedicine();
      await database.updateMedicine(medicine);
      update();
      Get.back();
      Get.snackbar(
        "Sucesso",
        "Medicamento atualizado com sucesso.",
        backgroundColor: Colors.green.withOpacity(0.8),
        colorText: Colors.white,
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      print("Error updating medicine: $e");
      print(e.toString());
      Get.snackbar(
        "Erro",
        "Não foi possível atualizar o medicamento: ${e.toString()}",
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      _isLoading.value = false;
    }
  }
}
