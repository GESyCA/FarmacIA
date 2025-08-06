import 'package:farmacia/app/controllers/add_medicine_controller.dart';
import 'package:farmacia/app/controllers/auth_controller.dart';
import 'package:farmacia/app/controllers/login_controller.dart';
import 'package:farmacia/app/controllers/medicine_controller.dart';
import 'package:farmacia/app/controllers/navigation_controller.dart';
import 'package:farmacia/app/controllers/profile_controller.dart';
import 'package:farmacia/app/controllers/register_controller.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:get/get.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class InitBindings implements Bindings {
  @override
  void dependencies() {
    Get.put(NavigationController(), permanent: true);
    Get.put(LoginController());
    Get.put(RegisterController());
    Get.put(AuthController(), permanent: true);
    Get.put(
      DatabaseService(
        client: Supabase.instance.client,
      ),
      permanent: true,
    );
    Get.put(
      ProfileController(),
    );
    Get.put(
      AddMedicineController(Get.find<DatabaseService>()),
    );
    Get.put(
      MedicineController(Get.find<DatabaseService>()),
    );
  }
}
