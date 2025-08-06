import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';

class EditController extends GetxController{ 
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final DatabaseService database;

  EditController(this.database);

  late final MedicineModel medicine;

  @override
  void onInit() {
    super.onInit();
    medicine = Get.arguments;
  }


  Future<void> updateMedicine() async {
    try {
      _isLoading.value = true;
      await database.updateMedicine(medicine);
      Get.snackbar(
        "Sucesso",
        "Medicamento atualizado com sucesso.",
        backgroundColor: Colors.green.withOpacity(0.8),
        colorText: Colors.white,
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      print("Error updating medicine: $e");
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
