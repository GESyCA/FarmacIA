import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AddMedicineController extends GetxController{

  // acesso ao banco de dados no supabase
  final DatabaseService databaseService = DatabaseService(client: Supabase.instance.client);

  // chave do formulario
  final GlobalKey<FormState> formKey = GlobalKey<FormState>();

  // variavel para controlar o estado de carregamento
  final isLoading = false.obs;
  
  // controladores de texto para os campos do formulario
  final TextEditingController dateController = TextEditingController();
  final TextEditingController dateEndController = TextEditingController();
  final TextEditingController doseController = TextEditingController();

  // lista de medicamentos, frequencias e formas farmaceuticas
  List<String> medicineList = [
    'Paracetamol',
    'Amoxicillina',
    'Amoxil',
    'Dramin',
    'Rivotril',
    'Tylenol',
    ];

  // coleta de medicamentos selecionados
    final RxString _selectedMedicine = ''.obs;
    String get selectedMedicine => _selectedMedicine.value;

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

  void setSelectedMedicine(String value) {
    _selectedMedicine.value = value;
  }

  List<String> formasFarmaceuticas = [
    'Comprimido',
    'Gotas',
    'Pomada',
  ];

  final RxString _selectedForma = ''.obs;
  String get selectedForma => _selectedForma.value;

}