import 'package:farmacia/app/data/models/hive/conversation_model.dart';
import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:hive/hive.dart';

class MedicineRepository extends GetxService {
  final DatabaseService database;
  final AuthService authService;

  MedicineRepository({required this.database, required this.authService});

  // A ÚNICA FONTE DA VERDADE!
  final RxList<MedicineModel> medicines = <MedicineModel>[].obs;

  final _isLoading = true.obs;
  bool get isLoading => _isLoading.value;

  late String _userId;

  // Método para inicializar o repositório
  Future<void> init() async {
    final user = await authService.getCurrentUser();
    _userId = user?.id ?? '';
    await fetchMedicines();
  }

  Future<void> fetchMedicines() async {
    try {
      _isLoading.value = true;
      final data = await database.getMedicines();
      medicines.assignAll(data); // Usa assignAll para substituir a lista e notificar os listeners
    } catch (e) {
      Get.snackbar(
        "Erro no Repositório",
        "Não foi possível carregar os medicamentos: ${e.toString()}",
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      _isLoading.value = false;
    }
  }

  Future<void> deleteMedicine(MedicineModel medicine) async {
    try {
      await database.deleteMedicine(medicine);

      // apagar conversas relacionadas a esse medicamento no hive
      final conversationBox = Hive.box<Conversation>('conversations');
      final String conversationKey = '${_userId}_${medicine.nome}';
      conversationBox.delete(conversationKey);

      // Remove da lista reativa. TODOS os controllers que usam essa lista serão notificados.
      medicines.remove(medicine);

      Get.snackbar(
        "Sucesso",
        "Medicamento excluído com sucesso.",
        backgroundColor: Colors.green.withOpacity(0.8),
      );
    } catch (e) {
      Get.snackbar(
        "Erro",
        "Não foi possível excluir o medicamento",
         backgroundColor: Colors.red.withOpacity(0.8),
      );
    }
  }
  
  // Adicione o método de adicionar aqui também
  Future<void> addMedicine(MedicineModel newMedicine) async {
      try {
        final savedMedicine = await database.registerMedicine(newMedicine);

        // Adiciona na nossa lista centralizada
        medicines.add(savedMedicine);
      } catch(e) {
         Get.snackbar(
        "Erro",
        "Não foi possível adicionar o medicamento",
         backgroundColor: Colors.red.withOpacity(0.8),
      );
      }
  }
}
