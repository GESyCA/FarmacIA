import 'package:farmacia/app/data/models/hive/conversation_model.dart';
import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/data/supabase/auth_service.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:hive/hive.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class MedicineController extends GetxController {
  // Define any necessary variables and methods for the medicine functionality here
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  final _isLoadingDelete = false.obs;
  bool get isLoadingDelete => _isLoadingDelete.value;

  // Add other necessary controllers and methods as needed
  final DatabaseService database;

  MedicineController(this.database);

  final RxList<MedicineModel> _medicines = <MedicineModel>[].obs;
  List<MedicineModel> get medicines => _medicines;

  final RxList<MedicineModel> _searchedItems = <MedicineModel>[].obs;
  List<MedicineModel> get searchedItems => _searchedItems;

  final Rx<TextEditingController> _searchController =
      TextEditingController().obs;
  TextEditingController get searchController => _searchController.value;

  final AuthService _authService = AuthService(client: Supabase.instance.client);

  late String _userId;
  String get userId => _userId;

  Future<List<MedicineModel>> fetchMedicines() async {
    try {
      final medicines = await database.getMedicines();
      return medicines;
    } catch (e) {
      print("Error fetching medicines: $e");
      Get.snackbar(
        "Erro",
        "Não foi possível carregar os medicamentos: ${e.toString()}",
        snackPosition: SnackPosition.BOTTOM,
      );
      return [];
    }
  }

  Future<void> deleteMedicine(MedicineModel medicine) async {
    try {
      _isLoadingDelete.value = true;
      await database.deleteMedicine(medicine);
      
      // apagar conversas relacionadas a esse medicamento no hive
      final conversationBox = Hive.box<Conversation>('conversations');
      final String conversationKey = '${_userId}_${medicine.nome}';
      conversationBox.delete(conversationKey);

      _medicines.remove(medicine);
      _searchedItems.remove(medicine);
      update();
      Get.back();
      Get.snackbar(
        "Sucesso",
        "Medicamento excluído com sucesso.",
        backgroundColor: Colors.green.withOpacity(0.8),
        colorText: Colors.white,
        snackPosition: SnackPosition.BOTTOM,
      );
    } catch (e) {
      print("Error deleting medicine: $e");
      Get.snackbar(
        "Erro",
        "Não foi possível excluir o medicamento: ${e.toString()}",
        backgroundColor: Colors.red.withOpacity(0.8),
        colorText: Colors.white,
        snackPosition: SnackPosition.BOTTOM,
      );
    } finally {
      _isLoadingDelete.value = false;
    }
  }

  Future<List<String>> getMedicinesName() async {
    return await database.getMedicineNames();
  }

  void filterSearchResults() {
    String query = _searchController.value.text.trim();
    if (query.isEmpty) {
      _searchedItems.assignAll(_medicines);
    } else {
      _searchedItems.assignAll(_medicines
          .where((medicine) =>
              medicine.nome.toLowerCase().contains(query.toLowerCase()))
          .toList());
    }
  }

  @override
  void onInit() async {
    // TODO: implement onInit
    super.onInit();
    _isLoading.value = true;

    final user = await _authService.getCurrentUser();
    _userId = user?.id ?? '';
    print('User ID: $_userId');

    _medicines.clear();
    final data = await fetchMedicines();
    _medicines.addAll(data);
    _searchedItems.value = _medicines.toList();
    _isLoading.value = false;
  }
}
