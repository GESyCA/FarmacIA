import 'package:farmacia/app/controllers/medicine_controller.dart';
import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class AddMedicineController extends GetxController {
  // acesso ao banco de dados no supabase
  final DatabaseService databaseService;

  AddMedicineController(this.databaseService);

  // chave do formulario
  final GlobalKey<FormState> formKey = GlobalKey<FormState>();

  // variavel para controlar o estado de carregamento
  final isLoading = false.obs;

  final _isInitialLoading = false.obs;
  bool get isInitialLoading => _isInitialLoading.value;

  // controladores de texto para os campos do formulario
  final TextEditingController dateController = TextEditingController();
  final TextEditingController dateEndController = TextEditingController();
  final TextEditingController doseController = TextEditingController();

  // lista de medicamentos, frequencias e formas farmaceuticas
  List<String> medicineList = [
    'Paracetamol',
    'Amoxicilina',
    'Amoxil',
    'Dramin',
    'Rivotril',
    'Tylenol',
  ];

  // coleta de medicamentos selecionados
  final RxString _selectedMedicine = ''.obs;
  String get selectedMedicine => _selectedMedicine.value;
  void setSelectedMedicine(String value) {
    _selectedMedicine.value = value;
  }

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

  List<String> formasFarmaceuticas = ['Comprimido', 'Gotas', 'Pomada'];

  final RxString _selectedForma = ''.obs;
  String get selectedForma => _selectedForma.value;
  void setSelectedForma(String value) {
    _selectedForma.value = value;
  }

  @override
  void onInit() async {
    super.onInit();
    await _initialMedicineFilter();

    setSelectedForma(formasFarmaceuticas.first);
    setSelectedFrequency(frequencia.first);
    setSelectedMedicine(medicineList.first);
  }

  @override
  void onClose() {
    dateController.dispose();
    dateEndController.dispose();
    doseController.dispose();
    super.onClose();
  }

  Future<void> createMedicine() async {
    if (formKey.currentState?.validate() ?? false) {
      isLoading.value = true;
      try {
        final nome = _selectedMedicine.value;
        final userId = Supabase.instance.client.auth.currentUser?.id ?? '';
        final receberNotificacao = _recieveNotification.value;
        final notificacoesPorDia =
            recieveNotification
                ? int.parse(_selectedFrequency.value.split(' ')[0])
                : null;
        final dose = doseController.text;
        final forma = _selectedForma.value;
        final inicioTratamento =
            indeterminate
                ? DateTime.now()
                : DateFormat('dd/MM/yyyy').parse(dateController.text);
        final fimTratamento =
            indeterminate
                ? null
                : DateFormat('dd/MM/yyyy').parse(dateEndController.text);

        final medicine = MedicineModel(
          id: null,
          userId: userId,
          nome: nome,
          receberNotificacao: receberNotificacao,
          notificacoesPorDia: notificacoesPorDia,
          dose: dose,
          forma: forma,
          inicioTratamento: inicioTratamento,
          fimTratamento: fimTratamento,
        );
        await databaseService.registerMedicine(medicine);
        print(medicine.toString());
        update();
        Get.back();
        Get.find<MedicineController>().onInit();
        Get.snackbar(
          'Sucesso',
          'Medicamento adicionado com sucesso!',
          snackPosition: SnackPosition.BOTTOM,
          backgroundColor: Colors.green.withOpacity(0.8),
          colorText: Colors.white,
        );
      } on FormatException catch (e) {
        Get.snackbar(
          'Erro',
          'Preencha data ou marque tempo indeterminado',
          snackPosition: SnackPosition.BOTTOM,
          backgroundColor: Colors.red.withOpacity(0.8),
          colorText: Colors.white,
        );
        print('Erro de formatação: $e');
      } catch (e) {
        Get.snackbar(
          'Erro',
          'Erro inesperado ao tentar adicionar o medicamento',
          snackPosition: SnackPosition.BOTTOM,
          backgroundColor: Colors.red.withOpacity(0.8),
          colorText: Colors.white,
        );
        print('Erro ao adicionar medicamento: $e');
      } finally {
        isLoading.value = false;
      }
    } else {
      Get.snackbar(
        'Erro',
        'Por favor, preencha todos os campos corretamente.',
        snackPosition: SnackPosition.BOTTOM,
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
      );
    }
  }

  Future<void> _initialMedicineFilter() async {
    _isInitialLoading.value = true;
    List<String> registedMedicines = await databaseService.getMedicineNames();
    if (registedMedicines.isNotEmpty) {
      // Atualiza a lista de medicamentos com os não registrados
      medicineList =
          medicineList
              .where((med) => !registedMedicines.contains(med))
              .toList();
    }

    _isInitialLoading.value = false;
    update();
  }
}
