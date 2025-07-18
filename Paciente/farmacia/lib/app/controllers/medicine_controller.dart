import 'package:farmacia/app/data/models/medicine_model.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class MedicineController extends GetxController {
  // Define any necessary variables and methods for the medicine functionality here
  final _isLoading = false.obs;
  bool get isLoading => _isLoading.value;

  // Add other necessary controllers and methods as needed
  final database = DatabaseService(client: Supabase.instance.client);

  final RxList<MedicineModel> _medicines = <MedicineModel>[].obs;
  List<MedicineModel> get medicines => _medicines;

  final RxList<MedicineModel> _searchedItems = <MedicineModel>[].obs;
  List<MedicineModel> get searchedItems => _searchedItems;

  final Rx<TextEditingController> _searchController = TextEditingController().obs;
  TextEditingController get searchController => _searchController.value;

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
  void onInit() async{
    // TODO: implement onInit
    super.onInit();
    _isLoading.value = true;
    _medicines.clear();
    final data = await fetchMedicines();
    _medicines.addAll(data);
    _searchedItems.value = _medicines.toList();
    _isLoading.value = false;
  }

}