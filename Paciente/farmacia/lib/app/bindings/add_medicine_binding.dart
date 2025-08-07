import 'package:farmacia/app/controllers/add_medicine_controller.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:get/get.dart';

class AddMedicineBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut<AddMedicineController>(
      () => AddMedicineController(Get.find<DatabaseService>()),
    );
  }
}