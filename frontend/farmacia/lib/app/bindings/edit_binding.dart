import 'package:farmacia/app/controllers/edit_controller.dart';
import 'package:farmacia/app/data/supabase/database_service.dart';
import 'package:get/get.dart';

class EditBinding extends Bindings {
  @override
  void dependencies() {
    Get.lazyPut(
      () => EditController(
        Get.find<DatabaseService>(),
      ),
    );
  }
}
